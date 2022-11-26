from bs4 import BeautifulSoup


with open("source/play-mbrlkbtq5jonaqkurjwmxftytyn2ethqvbxfu4rgjbkkknndqwae6byd.html") as fp:
    soup = BeautifulSoup(fp, "html.parser")
    print(soup.prettify())


