# Photo Battle

It is a Django application for organizing photo battles, a contest where teams compete for taking the best photos in a short time. This application acts as a host for the images, and a voting platform for electing the best pictures and the best teams.

## Getting Started

### Prerequisites

You'll need Python 3, and a [Django](https://www.djangoproject.com/) project.

### Installation

1. Install the release to the Python environment

    ```console
    pip install --extra-index-url="https://packages.chalier.fr" django-photobattle
    ```

2. Add `photobattle` to the `INSTALLED_APPS` variables in Django settings.py

    ```python
    INSTALLED_APPS = [
        '...',
        'photobattle',
        '...',
    ]
    ```  

3. Migrate the database

    ```console
    python manage.py migrate
    ```

4. Collect the new static files

    ```console
    python manage.py collectstatic
    ```

5. Setup the URLs

    ```python
    from django.urls import include
    import orgapy.urls
    urlpatterns = [
        ...,
        path("photo-battle/", include("photobattle.urls")),
    ]
    ```

6. Add an [ImgBB](https://fr.imgbb.com/) API key in the server settings: `PHOTOBATTLE_IMGBB_APIKEY = "..."` 

6. Reload your server, and it should be up.

### Permissions

The app uses Django built-in authentication framework, meaning that users need a Django account to created and edit notes. They also need to be granted Orgapy's permissions, such as `photobattle.add_battle` or `photobattle.change_battle`. On my server, I use a Django group for that matter.

## Built With

-  [Django](https://www.djangoproject.com/) - Web application framework for Python.

## Contributing

Contributions are welcomed. Push your branch and create a pull request detailling your changes.

## Authors

Project is maintained by [Yohan Chalier](https://chalier.fr).
