
# Exam board student management application

This project was developed as part of the requirements for obtaining the Bachelors of Science (Hons) qualitification.


## Run Locally

Clone the project

```bash
  git clone https://github.com/Kowalifwer/exam_board_app
```

Go to the project directory

```bash
  cd exam_board_app
```

Install dependencies

```bash
  pip install requirements.txt
```

Populate the database using the population script

```bash
  python manage.py populate.py
```

Start the server

```bash
  python manage.py runserver
```

Thats it! The web app should be up and running, so feel free to explore the different views.



## Running Tests

To run all the unit/integration tests, run the following command

```bash
  coverage run manage.py test
```

If you do not have coverage installed, run the following command. Note that it is recommended to run the tests with coverage, so you could generate the coverage report at the end.

```bash
  python manage.py test
```

IF you do not want selenium frontend tests to run, append  --exclude-tag=selenium, as follows
```bash
  coverage manage.py test --exclude-tag=selenium
```

To generate the coverage report run the following
```bash
  coverage html --omit=*/migrations/*,*/__init__.py,*/populate.py
```

The report can be found in the following directory
```bash
  /BASE_DIR(exam_board_app)/htmlcov/index.html
```
## Authors

- [@kowalifwer](https://www.github.com/kowalifwer)


## License

[MIT](https://choosealicense.com/licenses/mit/)

