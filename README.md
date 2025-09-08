# Django Ecommerce Project

This is a simple ecommerce web application built with Django.

## Features

- Product, Category, Customer, and Order models ([ecommerce/store/models.py](ecommerce/store/models.py))
- Admin interface for managing products and orders
- Basic templates (see [ecommerce/store/templates/](ecommerce/store/templates/))
- SQLite database for development

## Project Structure

```
ecommerce/
    manage.py
    ecommerce/
        settings.py
        urls.py
        ...
    store/
        models.py
        views.py
        templates/
        ...
requirements.txt
.gitignore
README.md
```

## Setup

1. **Clone the repository**

2. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

3. **Apply migrations**
   ```
   python ecommerce/manage.py migrate
   ```

4. **Create a superuser (optional, for admin access)**
   ```
   python ecommerce/manage.py createsuperuser
   ```

5. **Run the development server**
   ```
   python ecommerce/manage.py runserver
   ```

6. **Access the app**
   - Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

## Requirements

See [requirements.txt](requirements.txt).
