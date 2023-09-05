# Scraping News
Welcome to Scraping News v0.6.0

## Features
Scrapper:
- Detik
- Pikiran Rakyat

## Result
### Scrap Result

![Scrap Result](./files_result.png)

### Metadata Preview
![Metadata Preview](./metadata_preview.png)

### Data Preview
![Data Preview](./data_preview.png)

## Requirements
- Python 3.10.6
- Pip 22.3.1

## Installation

- Install the requirements of project
```bash
pip install -r requirements.txt 
```

- Run the program
```bash
python main.py
```

or

```
python main.py 2 "technology" 5 tech
```
The 1st argument you can choose between those menu:
1. Detik
2. Pikiran Rakyat
3. CNN Indonesia
4. Tribunnews
5. Kompas

The 2nd argument is the keyword you look after

The 3rd is how many pages you need the data

the 4th argument what folder name you'd like to save the scrap result

## Note

### Contribution
> Feel free to contribute to this open source project
> 
> If you need a new media to added to this project, feel free to
> fork and create a pull request
> 
> But keep in mind, to use [angular commit message convention](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#-commit-message-format)
> before you do pull request 

### Dynamic Websites
> There're several site that applying dynamic load data that
> beautifulsoup can't read the site at the first sight, needs to
> wait a couple second to fully load it
> 
> The sites are such as:
> - CNN Indonesia
> - Tribunnews
> - Kompas
> 
> So I used selenium to scrap the website that needed you to keep
> the display on to load all the pages else the progress will not
> processed
> 
> If you have a trouble with your internet, you can set the
> environment variable SELENIUM_WAIT_TIME to higher number, as
> it will set the wait time selenium tries to read the page you scrap

## Tested on
- Ubuntu 22.04.3 LTS

## Contributors
- Muchlish Choeruddin [Mcx002]