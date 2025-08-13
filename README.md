# American Pizza Project

Welcome to the American Pizza Project! 

The American Pizza Project is aimed at capturing the diverse philosophies and regional differences in pizza appreciation across the United States. We conducted  a series of pseudo nationally representiative interviews with participants from various backgrounds, focusing on their personal experiences and preferences related to pizza.

Each participant is asked to provide detailed responses (around 200 words) to the following questions about their personal pizza preferences and experiences:

Describe a turning point in your life when your taste or appreciation for pizza changed. Share the story or explain why there hasn't been a change.

Detail your ideal slice of pizza, including toppings, texture, sauce-cheese ratios, and your preferred regional style.

Explain when and how you typically eat pizza in your life—on the go, with others, etc.

Discuss the importance of pizza boxes and utensils to your pizza eating experience.

Share any experiences of being unable to eat pizza when you wanted to due to dietary reasons, cost, lack of availability, or other barriers.

Play with the Jupyter notebooks to examine how well Lloom extracts themes from the data in different conditions! The goal is to eventually expand exploration to include other themebuilding tools beyond Lloom as well.

Particularly interesting experimentation comes in choosing specific or broad seed theme terms and/or choosing different unit input chunks of data to be analyzed. Ex( q1 vs q1+q2 vs q1+q2+q3 vs all)
Note, if number of participants is too small or if seed theme is far fetched from responses, an error will occur.

The raw American Pizza Project Data (created with the help of Claude) as well as Lloom outputted theme summary examples are available in the data folder. Cloud dependant and locally runable lloom explorer notebooks are available in the Lloom_experiment_Jupyter_notebooks folder.


## Quick start
```bash
git clone https://github.com/<your-user>/AmericanPizzaProject.git
cd AmericanPizzaProject
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
python -m ipykernel install --user --name american-pizza --display-name "Python (american-pizza)"
