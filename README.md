# Local Payslip & Advance Slip Generator

A lightweight, local web application designed to automate the data entry, calculation, and precision printing of employee payslips and advance slips onto physical pre-printed forms. 

## Architecture
* **Backend:** Python (Flask)
* **Database:** Local `.csv` files (`employees.csv`, `sites.csv`)
* **Frontend:** Vanilla HTML, CSS, JavaScript
* **State Management:** Browser `sessionStorage` for real-time two-way form synchronization.

## Core Features
* **Automated Calculations:** Instantly calculates total salary based on daily rates, standard hours, OT, Sunday rates, allowances, and advance deductions.
* **Smart Autocomplete:** Fetches employee IC and Daily Rates dynamically from the local database as you type. Automatically learns and saves new Site locations.
* **Two-Way Data Sync:** Seamlessly shares data (Name, Date, Advance Amount) between the Payslip and Advance Slip generators without data loss on navigation.
* **Precision Print Alignment:** Uses absolute CSS positioning to map generated data directly into the blank boxes of pre-printed 7" x 7.5" physical paper slips.
* **Currency Splitting:** Automatically splits monetary values into whole numbers (Right-aligned) and decimals (Left-aligned) to fit specific printed column dividers.

## Prerequisites
* Python 3.x installed on the host machine.
* A modern web browser (Chrome/Edge recommended).

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <project-directory>
