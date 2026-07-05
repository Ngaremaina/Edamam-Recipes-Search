# Recipe Search Web Application
This web application is designed as a robust recipe search platform, leveraging the Django framework and seamlessly integrating the powerful Edamam API. By harnessing the capabilities of Django, it offers a solid foundation for handling user interactions and data management. Through the integration of the Edamam API, users can effortlessly explore a vast array of recipes tailored to their preferences and requirements. Whether searching for specific dishes or seeking culinary inspiration, this application provides a comprehensive and user-friendly experience for discovering delicious recipes.

## Features

- **Recipe Search**: Users can search for recipes by entering keywords or ingredients.
- **Recipe Details**: Users can view detailed information about each recipe, including ingredients, instructions, and nutritional information.
- **User Accounts**: Register/login/logout with password reset via email.
- **Search History**: Logged-in users can see a record of their past searches.
- **Favorites**: Logged-in users can save and remove recipes from a personal favorites list.

## Installation

1. Clone the repository:
   ```bash
      git clone https://github.com/Ngaremaina/Recipe-Search-Engine
      cd Recipe-Search-Engine
   ```
2. Intall the env variables
   ```bash
      python -m venv env
    ```

3. Activate the env file
   ```bash
      source env/bin/activate
   ```

4. Install dependencies:
   ```bash
      pip install -r requirements.txt
   ```

5. Build the Tailwind CSS (requires Node.js):
   ```bash
      npm install
      npm run build
   ```
   Use `npm run watch` instead while actively editing templates/styles to rebuild on save.

6. Apply database migrations:
   ```bash
      python manage.py migrate
   ```
   By default this uses local SQLite. To use a Neon (or any Postgres) database instead, set a
   `DATABASE_URL` env var, e.g. `postgresql://user:password@host/dbname?sslmode=require`.

7. Start the development server:
   ```bash
      python manage.py runserver
   ```

8. Open your web browser and go to `http://localhost:8000` to view the application.

### Environment variables

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `SECRET_KEY` | Yes | — | Django secret key |
| `EDAMAM_APP_ID` / `EDAMAM_APP_KEY` | Yes | — | Edamam recipe search API credentials |
| `DEBUG` | No | `True` | Set `False` in production |
| `DATABASE_URL` | No | local SQLite | Postgres/Neon connection string, without credentials, e.g. `postgresql://host/dbname?sslmode=require` |
| `DATABASE_USER` / `DATABASE_PASSWORD` | No | — | Credentials for `DATABASE_URL`, kept separate so they can be rotated/managed independently |
| `EMAIL_HOST` / `EMAIL_PORT` / `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` / `EMAIL_USE_TLS` | No | console backend | SMTP config for sending password reset emails; without these, reset emails are printed to the console |

## Usage

1. Use the search bar to enter keywords or ingredients for recipes you're looking for.
2. Browse through the search results and click on a recipe to view its details.
3. Register/log in to save recipes to your favorites and keep a history of your searches.

## Running Tests

```bash
python manage.py collectstatic --noinput  # needed once so templates can resolve {% static %} under test
python manage.py test
```

If `DATABASE_URL` points at a pooled Postgres connection (e.g. Neon's `-pooler` endpoint), add
`--keepdb`: `python manage.py test --keepdb`. Django's normal create/drop-test-database cycle can leave
an orphaned test database behind on a pooled connection since PgBouncer doesn't always release sessions
in time for the `DROP DATABASE` at teardown.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
