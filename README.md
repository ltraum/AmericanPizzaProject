# American Pizza Project

Welcome to the American Pizza Project! ![Lucille Ball Pizza](https://github.com/user-attachments/assets/30285ba0-a383-450b-832c-ec49ad75555c)


The American Pizza Project is aimed at capturing the diverse philosophies and regional differences in pizza appreciation across the United States. We conducted a nationally representiative set of pseudo interviews (Thanks Claude!). Each participant was asked to provide detailed responses (around 200 words) to the following questions about their personal pizza preferences and experiences:

1) Describe a turning point in your life when your taste or appreciation for pizza changed. Share the story or explain why there hasn't been a change.

2) Detail your ideal slice of pizza, including toppings, texture, sauce-cheese ratios, and your preferred regional style.

3) Explain when and how you typically eat pizza in your life—on the go, with others, etc.

4) Discuss the importance of pizza boxes and utensils to your pizza eating experience.

5) Share any experiences of being unable to eat pizza when you wanted to due to dietary reasons, cost, lack of availability, or other barriers.

At the crux of the American Pizza Project lies the goal of identifying themes of the pizza experience that carry relevence beyond any one individual. For this we can exlore computational tools! Play with the Jupyter notebooks to examine how well Lloom extracts themes from the data in different conditions! The hope is to eventually expand exploration to include other themebuilding tools beyond Lloom as well.

Particularly interesting experimentation comes in choosing specific or broad seed theme terms and/or choosing different unit input chunks of data to be analyzed. Ex( q1 vs q1+q2 vs q1+q2+q3 vs all)
Note, if number of participants is too small or if seed theme is too far-fetched from responses, an error will occur.

The raw American Pizza Project Data (Thanks again Claude!) as well as Lloom outputted theme summary examples are available in the data folder. Cloud dependant and locally runable lloom explorer notebooks are available in the Lloom_experiment_Jupyter_notebooks folder.


## Quick start
```bash
git clone https://github.com/<your-user>/AmericanPizzaProject.git
cd AmericanPizzaProject
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
python -m ipykernel install --user --name american-pizza --display-name "Python (american-pizza)"
