# OTP Auth Service (FastAPI + SQLite + Redis)

سرویس احراز هویت با ثبت‌نام مبتنی بر کد OTP پیامکی و لاگین دوگانه (شماره موبایل یا یوزرنیم + پسورد).

## امکانات
- ثبت‌نام با یوزرنیم، شماره موبایل و پسورد
- ارسال کد OTP و تأیید آن قبل از ساخت نهایی کاربر
- ذخیره‌ی دائمی کاربر در SQLite، و داده‌ی موقت OTP/ثبت‌نام در Redis (با TTL)
- لاگین با «شماره موبایل + پسورد» یا «یوزرنیم + پسورد»
- توکن JWT و اندپوینت محافظت‌شده‌ی `/auth/me`
- محدودیت تعداد تلاش اشتباه و cooldown برای ارسال مجدد

## تکنولوژی‌ها
FastAPI · APIRouter · Pydantic v2 / pydantic-settings · SQLAlchemy 2.0 + SQLite · Redis · passlib(bcrypt) · python-jose(JWT)

## ساختار
```
otp_auth/
├── requirements.txt
├── .env.example
├── docker-compose.yml
└── app/
    ├── main.py
    ├── database.py
    ├── core/        (config, security, redis_client)
    ├── models/      (user)
    ├── schemas/     (auth)
    ├── services/    (otp)
    └── routers/     (auth)
```

## اجرا (محلی)
```bash
cd otp_auth
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # or you can use uv "uv sync"
cp .env.example .env          # SECRET_KEY را عوض کن
# Redis باید بالا باشد:
docker run -d -p 6379:6379 redis:7-alpine
uvicorn app.main:app --reload
```
مستندات تعاملی: http://localhost:8000/docs

## اجرا با Docker Compose
```bash
docker compose up --build
```
## خلاصه کارکرد
 موقع ثبت نام یک کد موقت و اطلاعات وارد شده در ردیس ذخیره می شوند و بعد از عملیات verify اطلاعات در sqlite کامیت میشوند و یک jwt ساخته میشود .
 همچنین بعد از ثبت نام میتوان هم با شماره و هم با یوزرنیم jwt گرفت و وارد حساب کاربری شد
## مسیر استفاده (Flow)
1. `POST /auth/register` → یوزرنیم/شماره/پسورد ⟶ کد OTP تولید می‌شود (در حالت debug در `debug_otp` برمی‌گردد)
2. `POST /auth/verify-otp` → شماره + کد ⟶ کاربر در SQLite ساخته و توکن JWT داده می‌شود
3. `POST /auth/resend-otp` → ارسال مجدد کد با رعایت cooldown
4. `POST /auth/login/phone` → لاگین با شماره + پسورد
5. `POST /auth/login/username` → لاگین با یوزرنیم + پسورد
6. `GET /auth/me` → اطلاعات کاربر (نیازمند `Authorization: Bearer <token>`)


## نمونه‌ی cURL
```bash
# 1) register
curl -X POST localhost:8000/auth/register -H 'content-type: application/json' \
  -d '{"username":"ali","phone":"+989121234567","password":"secret123"}'

# 2) verify (code از پاسخ مرحله قبل / لاگ سرور)
curl -X POST localhost:8000/auth/verify-otp -H 'content-type: application/json' \
  -d '{"phone":"+989121234567","code":"123456"}'

# 3) login with phone
curl -X POST localhost:8000/auth/login/phone -H 'content-type: application/json' \
  -d '{"phone":"+989121234567","password":"secret123"}'
```

## ⚠️ نکته‌ی امنیتی
فیلد `debug_otp` در پاسخ فقط برای تست محلی است. در پروداکشن `DEBUG=false` بگذار و کد را در توابع
`register` / `resend_otp` (فایل `app/routers/auth.py`) به‌جای print، با درگاه پیامک واقعی
(کاوه‌نگار، قاصدک، Twilio و ...) ارسال کن. همچنین حتماً `SECRET_KEY` را عوض کن.
