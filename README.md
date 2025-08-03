# 🏛️ Court-Data Fetcher & Mini-Dashboard

A lightweight web app to fetch Indian court case metadata and latest orders/judgments by case type, number, and filing year.

---

## ✅ Court Targeted

**Delhi High Court**  
Website: [https://delhihighcourt.nic.in/](https://delhihighcourt.nic.in/)

---

## 🎯 Functional Features

- Case lookup by **Case Type**, **Case Number**, and **Filing Year**
- CAPTCHA image auto-solved using 2Captcha API
- Extracts:
  - Parties' names
  - Filing & next hearing dates
  - Latest order/judgment PDF (downloadable)
- Query log and raw HTML saved to SQLite database
- User-friendly error handling and clean UI

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/court-fetcher.git
cd court-fetcher
