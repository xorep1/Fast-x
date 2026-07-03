# OTP Auth Service (FastAPI + SQLite + Redis)

سرویس احراز هویت با ثبت‌نام مبتنی بر کد OTP پیامکی و لاگین دوگانه (شماره موبایل یا یوزرنیم + پسورد).

## امکانات
- ثبت‌نام با یوزرنیم، شماره موبایل و پسورد
- ارسال کد OTP و تأیید آن قبل از ساخت نهایی کاربر
- ذخیره‌ی دائمی کاربر در SQLite، و داده‌ی موقت OTP/ثبت‌نام در Redis (با TTL)
- لاگین با «شماره موبایل + پسورد» یا «یوزرنیم + پسورد»
- **Access token + Refresh token** با چرخش (rotation) و امکان باطل‌سازی در Redis
- **ویرایش پروفایل** بعد از لاگین: ایمیل، نام کامل، آدرس (به‌روزرسانی جزئی)
- تغییر پسورد (که همه‌ی نشست‌های قبلی را باطل می‌کند)
- **Alembic** برای مدیریت مهاجرت دیتابیس
- **پنل ادمین** (`/admin`): مشاهده‌ی کاربران، نشست‌های فعال (refresh tokenها)، مصرف CPU/RAM/دیسک و وضعیت آنلاین بودن Redis و دیتابیس
- محدودیت تعداد تلاش اشتباه و cooldown برای ارسال مجدد

## پنل ادمین
یک داشبورد تحت‌وب در آدرس `/admin`:
```
http://localhost:8000/admin
```
امکانات:
- 📊 مصرف زنده‌ی CPU، RAM و دیسک (به‌روزرسانی خودکار هر ۱۰ ثانیه)
- 🟢 وضعیت up/down بودن Redis و دیتابیس با latency
- 👥 لیست همه‌ی کاربران + فعال/غیرفعال کردن
- 🔑 لیست همه‌ی نشست‌های فعال با جزئیات کامل: **ساعت ورود، IP، نوع دستگاه، سیستم‌عامل، مرورگر** + باطل کردن تکی یا گروهی
- 🚫 **بن کردن کاربر** برای مدت دلخواه (دقیقه) یا دائمی، همراه با **دلیل**. کاربر بن‌شده هنگام هر درخواست، دلیل و زمان پایان بن را در پاسخ ۴۰۳ می‌بیند.

**ساخت کاربر ادمین** (بعد از `alembic upgrade head`):
```bash
# ساخت ادمین جدید:
python -m scripts.create_admin admin +989120000000 yourpassword
# یا ارتقای یک کاربر موجود به ادمین:
python -m scripts.create_admin --promote <username_or_phone>
```
سپس در `/admin` با همان حساب وارد شو. فقط حساب‌هایی که `is_admin=True` دارند اجازه‌ی ورود دارند.

## تکنولوژی‌ها
FastAPI · APIRouter · Pydantic v2 / pydantic-settings · SQLAlchemy 2.0 + SQLite · Alembic · Redis · bcrypt · python-jose(JWT) · psutil

## مهاجرت دیتابیس (Alembic)
قبل از اولین اجرا، جدول‌ها را با مهاجرت بساز:
```bash
alembic upgrade head
```
برای ساخت مهاجرت جدید بعد از تغییر مدل‌ها:
```bash
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

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
pip install -r requirements.txt
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

## مسیر استفاده (Flow)
1. `POST /auth/register` → یوزرنیم/شماره/پسورد ⟶ کد OTP تولید می‌شود (در حالت debug در `debug_otp` برمی‌گردد)
2. `POST /auth/verify-otp` → شماره + کد ⟶ کاربر ساخته و **access + refresh token** داده می‌شود
3. `POST /auth/resend-otp` → ارسال مجدد کد با رعایت cooldown
4. `POST /auth/login/phone` → لاگین با شماره + پسورد ⟶ access + refresh
5. `POST /auth/login/username` → لاگین با یوزرنیم + پسورد ⟶ access + refresh
6. `POST /auth/refresh` → refresh token ⟶ جفت توکن جدید (توکن قبلی باطل می‌شود)
7. `POST /auth/logout` → refresh token ⟶ باطل‌سازی همان نشست
8. `GET /auth/me` → خواندن اطلاعات کاربر (نیازمند `Authorization: Bearer <access_token>`)
9. `PATCH /auth/me` → ویرایش پروفایل (ایمیل/نام/آدرس؛ فقط فیلدهای ارسالی تغییر می‌کنند)
10. `POST /auth/change-password` → تغییر پسورد (همه‌ی نشست‌ها باطل می‌شوند)

### درباره‌ی access و refresh token
- **access token**: کوتاه‌عمر (پیش‌فرض ۶۰ دقیقه). در هدر هر درخواست فرستاده می‌شود.
- **refresh token**: بلندعمر (پیش‌فرض ۷ روز). فقط برای گرفتن access token جدید از `/auth/refresh`.
- هر بار refresh، توکن قبلی باطل و یک جفت جدید صادر می‌شود (rotation).
- شناسه‌ی refresh token در Redis نگه داشته می‌شود تا بتوان آن را باطل کرد (logout / تغییر پسورد).

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
