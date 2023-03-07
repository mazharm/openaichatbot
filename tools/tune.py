"""
This tool uses a genetic algorithm to tune the hyperparameters of the GPT-3 model.
It uses two methods to evaluate the fitness of a hyperparameter set: 
(1) the perplexity of the generated text and 
(2) the cosine similarity between the generated text and the target response.

The fitness function is a weighted sum of the two methods. The tools invokes the algorithm with 
different weights to find the optimal hyperparameters. The final judgement of the optimal
hyperparameters is based on the human judgement of the generated text.
"""
import random
import json
from sklearn.metrics.pairwise import cosine_similarity
from .openaicli import OpenAICli

with open('training_data.json', 'r', encoding='utf-8') as file:
    training_data = json.load(file)

oac = OpenAICli()

# Define the hyperparameters
temperature_range = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
top_p_range = [0.5, 0.7, 0.9, 1]
frequency_penalty_range = [0, 0.2, 0.4, 0.6, 0.8, 1.2, 1.4, 1.6, 1.8, 2]
presence_penalty_range = [0, 0.2, 0.4, 0.6, 0.8, 1.2, 1.4, 1.6, 1.8, 2]

# Define the fitness function
def fitness(hyperparameters, messages, target_response, perplexity_weight, similarity_weight):
    generated_text, perplexity = oac.get_response(messages,hyperparameters)

    generated_vector = oac.get_embedding(generated_text)
    target_vector = oac.get_embedding(target_response)
    similarity = cosine_similarity(generated_vector.reshape(1,-1), target_vector.reshape(1,-1))
    score = perplexity_weight * (1.0 / float(perplexity)) + similarity_weight * similarity[0][0]

    return score

# Generate the initial population
def generate_individual():
    temperature = random.choice(temperature_range)
    top_p = random.choice(top_p_range)
    frequency_penalty = random.choice(frequency_penalty_range)
    presence_penalty = random.choice(presence_penalty_range)

    return {'temperature': temperature, 'top_p': top_p, 'frequency_penalty': frequency_penalty, 'presence_penalty': presence_penalty}


def generate_population(population_size=100):
    population = [generate_individual() for _ in range(population_size)]

    return population

def evaluate_population(population, perplexity_weight, similarity_weight):
    fitness_scores = []
    for individual in population:
        prompt = random.choice(training_data['prompt'])
        target_response = training_data.loc[training_data['prompt'] == prompt, 'response'].values[0]
        score = fitness(individual, prompt, target_response, perplexity_weight, similarity_weight)
        fitness_scores.append(score)

    return fitness_scores

def evolve_population(population, population_size, fitness_scores):
    # Selection
    num_selected = int(population_size * 0.2)
    selected_indices = sorted(range(population_size), key=lambda i: fitness_scores[i], reverse=True)[:num_selected]
    selected_population = [population[i] for i in selected_indices]

    # Crossover
    new_population = []
    while len(new_population) < population_size:
        parent1 = random.choice(selected_population)
        parent2 = random.choice(selected_population)
        child = {}
        for key in parent1.keys():
            if random.random() < 0.5:
                child[key] = parent1[key]
            else:
                child[key] = parent2[key]
        new_population.append(child)

    # Mutation
    for individual in new_population:
        if random.random() < 0.1:
            individual['temperature'] = random.choice(temperature_range)
        if random.random() < 0.1:
            individual['top_p'] = random.choice(top_p_range)
        if random.random() < 0.1:
            individual['frequency_penalty'] = random.choice(frequency_penalty_range)
        if random.random() < 0.1:
            individual['presence_penalty'] = random.choice(presence_penalty_range)

    return new_population

def run_genetic_algorithm(population_size=100, num_generations=10, perplexity_weight=0.5, similarity_weight=0.5):
    population = generate_population(population_size)
    fitness_scores = evaluate_population(population, perplexity_weight, similarity_weight)

    # Evolution loop
    num_generations = 10
    for generation in range(num_generations):
        print('Generation:', generation)
        new_population = evolve_population(population, population_size, fitness_scores)

        # Evaluate the fitness of the new population
        new_fitness_scores = evaluate_population(new_population, perplexity_weight, similarity_weight)

        # Replace the old population with the new population
        population = new_population
        fitness_scores = new_fitness_scores

        best_index = fitness_scores.index(max(fitness_scores))
        best_individual = population[best_index]
        
        print(f"Generation:{generation}, Best individual:{best_individual}")

    return best_individual

if __name__ == '__main__':
    weights = {(0, 1), (1, 0), (0.25, 0.75), (0.75, 0.25), (0.5, 0.5)}

    for weight in weights:
        perplexity_weight, similarity_weight = weight
        best_individual = run_genetic_algorithm(100, 10, perplexity_weight, similarity_weight)
        print(f'perplexity_weight:{perplexity_weight}, similarity_weight:{similarity_weight}, Best individual:{best_individual}')
