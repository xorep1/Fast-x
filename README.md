<div align="center">

# ⚡ Fast-x

**سرویس احراز هویت مبتنی بر OTP با پنل مدیریت**

یک boilerplate آمادهٔ پروداکشن برای احراز هویت با کد یک‌بار‌مصرف پیامکی (OTP)،
لاگین دوگانه، مدیریت نشست‌ها (session) و یک پنل ادمین کامل.

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.11x-009688?logo=fastapi&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

</div>

---

## 📖 معرفی

**Fast-x** یک سرویس احراز هویت (Authentication) کامل و ماژولار است که با **FastAPI** ساخته شده.
هستهٔ آن بر پایهٔ ثبت‌نام با **کد OTP پیامکی** است و از لاگین دوگانه پشتیبانی می‌کند:
«شمارهٔ موبایل + پسورد» یا «یوزرنیم + پسورد».

اطلاعات دائمی کاربران در **SQLite** (قابل تعویض با هر دیتابیس SQLAlchemy) ذخیره می‌شود
و داده‌های موقت مثل کدهای OTP، نشست‌های refresh، محدودیت‌ها و ban ها در **Redis** با TTL نگهداری می‌شوند.

> 💡 این پروژه به‌عنوان یک نقطهٔ شروع (boilerplate) طراحی شده — می‌توانید سرویس واقعی ارسال پیامک، دیتابیس تولیدی و منطق دامنهٔ خودتان را روی آن سوار کنید.

---

## ✨ امکانات

### 🔐 احراز هویت
- ثبت‌نام با **یوزرنیم، شمارهٔ موبایل و پسورد**
- ارسال و **تأیید کد OTP** پیش از ساخت نهایی کاربر (کاربر فقط بعد از verify واقعاً ساخته می‌شود)
- لاگین با **«موبایل + پسورد»** یا **«یوزرنیم + پسورد»**
- پشتیبانی از فرم استاندارد OAuth2 (`/auth/token`) برای سازگاری با Swagger UI
- توکن **JWT** جداگانه برای access و refresh با تفکیک نوع توکن (type claim)
- **چرخش توکن (Refresh Token Rotation)**: هر refresh یک توکن جدید صادر و توکن قبلی را باطل می‌کند

### 🛡️ امنیت و محدودیت‌ها
- هش پسورد با **bcrypt**
- **محدودیت تعداد تلاش اشتباه** OTP و **cooldown** برای ارسال مجدد
- **محدودیت تعداد نشست‌های همزمان** هر کاربر (حذف قدیمی‌ترین نشست هنگام عبور از سقف)
- **باطل‌سازی نشست**‌ها: خروج تکی، خروج از همهٔ دستگاه‌ها (مثلاً بعد از تغییر پسورد)
- **نرمال‌سازی خودکار شمارهٔ موبایل** ایران (`09...` → `+98...`)

### 👤 پروفایل کاربر
- endpoint محافظت‌شدهٔ `/auth/me`
- ویرایش جزئی پروفایل (ایمیل، نام کامل، آدرس)
- تغییر پسورد (با باطل شدن همهٔ نشست‌های فعال)

### 🧑‍💼 پنل ادمین
- رابط HTML آماده روی مسیر `/admin`
- آمار کلی، **مانیتورینگ منابع سیستم** (CPU / RAM / Disk) و health چک سرویس‌ها (Redis + DB)
- لیست کاربران، **بن/آنبن** (موقت با TTL یا دائمی)، فعال/غیرفعال‌سازی
- مشاهدهٔ نشست‌های فعال به همراه **IP، مرورگر، سیستم‌عامل و نوع دستگاه** و باطل‌سازی آن‌ها

---

## 🧱 پشتهٔ فناوری (Tech Stack)

| لایه | فناوری |
|------|--------|
| Web framework | FastAPI + Uvicorn |
| ORM / دیتابیس | SQLAlchemy 2.0 + SQLite |
| کش / داده موقت | Redis |
| مهاجرت دیتابیس | Alembic |
| احراز هویت | python-jose (JWT) + bcrypt |
| اعتبارسنجی | Pydantic v2 + pydantic-settings |
| مانیتورینگ | psutil |
| تشخیص دستگاه | user-agents |
| استقرار | Docker + docker-compose |

---

## 📂 ساختار پروژه

```
Fast-x/
├── app/
│   ├── main.py               # نقطهٔ ورود FastAPI
│   ├── database.py           # اتصال SQLAlchemy و Session
│   ├── core/
│   │   ├── config.py         # تنظیمات از .env
│   │   ├── security.py       # هش پسورد + JWT
│   │   ├── redis_client.py   # کلاینت Redis
│   │   └── request_info.py   # استخراج IP/مرورگر/دستگاه
│   ├── models/user.py        # مدل ORM کاربر
│   ├── schemas/auth.py       # اسکیمای Pydantic
│   ├── routers/
│   │   ├── auth.py           # مسیرهای احراز هویت
│   │   └── admin.py          # مسیرهای پنل ادمین
│   ├── services/
│   │   ├── otp.py            # منطق OTP + ثبت‌نام معلق
│   │   ├── tokens.py         # مدیریت نشست‌های refresh
│   │   ├── bans.py           # مدیریت بن کاربران
│   │   └── monitoring.py     # آمار سیستم و سلامت سرویس‌ها
│   └── static/admin.html     # رابط پنل ادمین
├── migrations/               # مهاجرت‌های Alembic
├── scripts/create_admin.py   # ساخت/ارتقای کاربر ادمین
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## 🚀 راه‌اندازی

### پیش‌نیازها
- Python **3.11+**
- **Redis** در حال اجرا (لوکال یا از طریق Docker)

### روش ۱ — اجرای محلی

```bash
# 1) کلون پروژه
git clone https://github.com/xorep1/Fast-x.git
cd Fast-x

# 2) محیط مجازی و نصب وابستگی‌ها
python -m venv .venv
source .venv/bin/activate        # ویندوز: .venv\Scripts\activate
pip install -r requirements.txt

# 3) ساخت فایل تنظیمات
cp .env.example .env
# مقدار SECRET_KEY را حتماً تغییر دهید!

# 4) اعمال مهاجرت‌های دیتابیس
alembic upgrade head

# 5) اجرای سرور
uvicorn app.main:app --reload
```

سرویس روی `http://localhost:8000` بالا می‌آید:
- 📘 مستندات Swagger: `http://localhost:8000/docs`
- 🧑‍💼 پنل ادمین: `http://localhost:8000/admin`

### روش ۲ — با Docker Compose

```bash
cp .env.example .env      # SECRET_KEY را تنظیم کنید
docker compose up --build
```

این دستور همزمان Redis و سرویس API را بالا می‌آورد.

### ساخت کاربر ادمین

```bash
# ساخت کاربر ادمین جدید
python -m scripts.create_admin <username> <phone> <password>

# یا ارتقای یک کاربر موجود به ادمین
python -m scripts.create_admin --promote <username_or_phone>
```

---

## ⚙️ تنظیمات (متغیرهای محیطی)

| متغیر | پیش‌فرض | توضیح |
|-------|---------|-------|
| `APP_NAME` | `OTP Auth Service` | نام اپلیکیشن |
| `DEBUG` | `true` | حالت دیباگ |
| `DATABASE_URL` | `sqlite:///./otp_auth.db` | آدرس دیتابیس |
| `REDIS_URL` | `redis://localhost:6379/0` | آدرس Redis |
| `max_session` | `3` | سقف نشست‌های همزمان هر کاربر |
| `SECRET_KEY` | — | **کلید امضای JWT (حتماً عوض شود!)** |
| `ALGORITHM` | `HS256` | الگوریتم JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | عمر access token |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | عمر refresh token |
| `OTP_LENGTH` | `6` | طول کد OTP |
| `OTP_TTL_SECONDS` | `120` | اعتبار کد OTP |
| `OTP_RESEND_COOLDOWN` | `60` | حداقل فاصله بین دو درخواست OTP |
| `OTP_MAX_ATTEMPTS` | `5` | حداکثر تلاش اشتباه قبل از باطل شدن کد |
| `REGISTRATION_TTL_SECONDS` | `600` | مدت نگهداری دادهٔ ثبت‌نام معلق |

---

## 🔗 مسیرهای API

### احراز هویت (`/auth`)

| متد | مسیر | توضیح |
|-----|------|-------|
| `POST` | `/auth/register` | شروع ثبت‌نام و ارسال OTP |
| `POST` | `/auth/verify-otp` | تأیید OTP و ساخت نهایی کاربر (بازگشت توکن) |
| `POST` | `/auth/resend-otp` | ارسال مجدد OTP (با رعایت cooldown) |
| `POST` | `/auth/login/phone` | لاگین با موبایل + پسورد |
| `POST` | `/auth/login/username` | لاگین با یوزرنیم + پسورد |
| `POST` | `/auth/token` | لاگین فرم OAuth2 (برای Swagger) |
| `POST` | `/auth/refresh` | تعویض refresh token و صدور توکن جدید |
| `POST` | `/auth/logout` | خروج (باطل‌سازی نشست فعلی) |
| `GET`  | `/auth/me` | دریافت پروفایل کاربر جاری |
| `PATCH`| `/auth/me` | ویرایش جزئی پروفایل |
| `POST` | `/auth/change-password` | تغییر پسورد (خروج از همهٔ نشست‌ها) |

### پنل ادمین (`/admin`)

| متد | مسیر | توضیح |
|-----|------|-------|
| `GET`  | `/admin` | رابط HTML پنل ادمین |
| `GET`  | `/admin/stats` | آمار کلی |
| `GET`  | `/admin/health` | سلامت سرویس‌ها (Redis + DB) |
| `GET`  | `/admin/users` | لیست کاربران |
| `POST` | `/admin/users/{id}/ban` | بن کاربر (موقت یا دائم) |
| `POST` | `/admin/users/{id}/unban` | آنبن کاربر |
| `POST` | `/admin/users/{id}/toggle-active` | فعال/غیرفعال‌سازی |
| `GET`  | `/admin/tokens` | لیست نشست‌های فعال |
| `POST` | `/admin/tokens/revoke` | باطل‌سازی یک نشست |
| `POST` | `/admin/users/{id}/revoke-all` | باطل‌سازی همهٔ نشست‌های کاربر |

---

## 🔄 جریان ثبت‌نام

```
register  ──►  ارسال OTP  ──►  verify-otp  ──►  ساخت کاربر + صدور توکن
   │                              ▲
   └──────  resend-otp  ──────────┘   (با رعایت cooldown)
```

نمونهٔ درخواست ثبت‌نام:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"ali","phone":"09123456789","password":"secret123"}'
```

---

## ⚠️ نکات مهم پروداکشن

- 🔑 حتماً `SECRET_KEY` را در `.env` عوض کنید و آن را در گیت commit نکنید.
- 📵 در حالت واقعی، فیلد `debug_otp` که کد OTP را در پاسخ برمی‌گرداند **باید حذف شود** — این مورد فقط برای تست/دمو گذاشته شده است.
- 📨 سرویس واقعی ارسال پیامک (SMS gateway) را جایگزین منطق فعلی OTP کنید.
- 🗄️ برای بار بالا، SQLite را با PostgreSQL/MySQL جایگزین کنید (فقط `DATABASE_URL` را تغییر دهید).
- 🌐 پشت یک reverse proxy (مثل Nginx) با HTTPS مستقر کنید.

---

## 📝 لایسنس

این پروژه تحت لایسنس **MIT** منتشر شده است.

---

<div align="center">
ساخته‌شده با ⚡ FastAPI
</div>
