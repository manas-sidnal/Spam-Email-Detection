# **Spam Email Detection**

This project trains a machine-learning model to classify emails as **spam** or **ham**.
All processing, feature extraction, model training, and evaluation are done inside:

```
notebooks/eda.ipynb
```

---

## **Project Structure**

```
Spam email detection/
|-.venv/                  # NOT included in repo.
|-data/                   # NOT included in repo; user must download
|   |-ham/
|   |-spam/
|-notebooks/
|   |-eda.ipynb
|-src/
|   |-check_env.py
|   |-load_emails.py
|-.gitignore
|-README.md
|-requirements.txt
```

---

The dataset itself is **NOT included in the repository**
**Anyone cloning the repo must download and extract the dataset manually using the instructions below.**

# **How to Get the Dataset**

Follow these steps:

### 1️⃣ Download SpamAssassin archives manually:

Download from Apache’s public corpus

### 2️⃣ Create the expected structure:

Inside the project folder create:

```
data/
   spam/
   ham/
```

### 3️⃣ Extract files:

* Extract all **spam archives** into:
  `data/spam/`

* Extract all **ham archives** into:
  `data/ham/`

After extraction, you should have thousands of raw email files in each folder.

---

# **What the Project Does**

1. Loads raw email files from `data/spam` + `data/ham`.
2. Extracts:

   * Subject
   * From / To / Date
   * Plain-text body (handles multipart + HTML)
3. Normalizes text (`<URL>`, `<EMAIL>` replacements).
4. Builds a combined field:

   ```
   text = subject + " " + body
   ```
5. Extracts TF-IDF features (unigrams + bigrams, 5000 features).
6. Trains:

   * Multinomial Naive Bayes
   * Logistic Regression
7. Evaluates using:

   * Classification report
   * Confusion matrix

All inside `notebooks/eda.ipynb`.

---

# **Model Performance (Summary)**

### Logistic Regression (best)

* Spam Precision ≈ **0.98**
* Spam Recall ≈ **0.86**
* Spam F1 ≈ **0.92**

### Naive Bayes (baseline)

* Spam F1 ≈ **0.89**

---

# **How to Run**

### **1. Create virtual environment**

```powershell
python -m venv .venv
```

### **2. Activate virtual environment**

```powershell
.\.venv\Scripts\Activate.ps1
```

### **3. Install dependencies**

```powershell
pip install -r requirements.txt
```

### **4. Ensure `data/ham` and `data/spam` are correctly populated**

(as described above)

### **5. Open the notebook**

```
notebooks/eda.ipynb
```

---