import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import os

def get_random_animals(count):
    animals = ['Lion', 'Eagle', 'Dolphin', 'Wolf', 'Elephant', 'Giraffe', 'Penguin', 'Bear', 'Fox', 'Owl']
    return random.sample(animals, count)

def save_user_data(name, skills_data, interests_data):
    filename = f"{name.lower().replace(' ', '_')}_persona.json"
    user_data = {
        'name': name,
        'skills': skills_data,
        'interests': interests_data
    }
    with open(filename, 'w') as f:
        json.dump(user_data, f, indent=2)
    return filename

def load_user_data(name):
    filename = f"{name.lower().replace(' ', '_')}_persona.json"
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return None

def get_user_choice():
    while True:
        choice = input("Do you want to (1) create new profile or (2) edit existing profile? ").strip()
        if choice in ['1', '2']:
            return choice
        print("Please enter 1 or 2.")

def get_rating(animal, metric):
    while True:
        try:
            rating = int(input(f"{animal} {metric} (1=Low, 5=High): "))
            if 1 <= rating <= 5:
                return rating
            else:
                print("Please enter a number between 1 and 5.")
        except ValueError:
            print("Please enter a valid number.")

def create_radar_chart(skills_df, interests_df, name):
    # Create figure with polar subplot
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    # Number of variables
    categories = skills_df['Animal'].tolist()
    N = len(categories)
    
    # Angles for each axis
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Complete the loop
    
    # Skills values
    skill_values = skills_df['Skill'].tolist()
    skill_values += skill_values[:1]  # Complete the loop
    
    # Interest values
    interest_values = interests_df['Interest'].tolist()
    interest_values += interest_values[:1]  # Complete the loop
    
    # Plot skills (red)
    ax.plot(angles, skill_values, 'o-', linewidth=2, color='red', alpha=0.7, label='Skills')
    ax.fill(angles, skill_values, alpha=0.25, color='red')
    
    # Plot interests (green)
    ax.plot(angles, interest_values, 's-', linewidth=2, color='green', alpha=0.7, label='Interests')
    ax.fill(angles, interest_values, alpha=0.25, color='green')
    
    # Add labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=12)
    
    # Set y-axis limits
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(['1', '2', '3', '4', '5'], fontsize=10)
    
    # Add grid
    ax.grid(True, alpha=0.3)
    
    # Add legend
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=12)
    
    # Title
    plt.title(f"{name}'s Persona Profile\nSkills vs Interests Radar Chart", 
             size=16, weight='bold', pad=20)
    
    plt.tight_layout()
    return fig

def run_survey():
    print("🎯 Persona Profile Survey\n")
    
    name = input("What is your name? ")
    
    # Check if user wants to load existing data
    existing_data = load_user_data(name)
    
    if existing_data:
        print(f"\nFound existing profile for {name}!")
        choice = get_user_choice()
        
        if choice == '2':  # Edit existing
            print("\nCurrent profile:")
            skills_df = pd.DataFrame(existing_data['skills'])
            interests_df = pd.DataFrame(existing_data['interests'])
            combined_df = skills_df.merge(interests_df, left_on='Animal', right_on='Animal')
            print(combined_df.to_string(index=False))
            
            # Create radar chart
            fig = create_radar_chart(skills_df, interests_df, name)
            plt.savefig(f'{name}_persona_radar.png', dpi=300, bbox_inches='tight')
            print(f"\n🎯 Radar chart saved as '{name}_persona_radar.png'")
            plt.show()
            return
    
    # Create new profile
    print(f"\nHello, {name}! Please rate your skill level for each animal (1-5):\n")
    
    random_animals = get_random_animals(5)
    skills_data = []
    
    for animal in random_animals:
        rating = get_rating(animal, "skill")
        skills_data.append({'Animal': animal, 'Skill': rating})
    
    print(f"\nNow rate your interest level for each animal (1-5):\n")
    
    interests_data = []
    for animal in random_animals:
        rating = get_rating(animal, "interest")
        interests_data.append({'Animal': animal, 'Interest': rating})
    
    # Create pandas DataFrames
    skills_df = pd.DataFrame(skills_data)
    interests_df = pd.DataFrame(interests_data)
    
    # Combine for display
    combined_df = skills_df.merge(interests_df, on='Animal')
    
    print("\n📊 Your Persona Profile:")
    print(f"Name: {name}")
    print(combined_df.to_string(index=False))
    
    # Save user data
    filename = save_user_data(name, skills_data, interests_data)
    print(f"\n💾 Profile saved to {filename}")
    
    # Create radar chart
    fig = create_radar_chart(skills_df, interests_df, name)
    
    # Save and show the chart
    plt.savefig(f'{name}_persona_radar.png', dpi=300, bbox_inches='tight')
    print(f"🎯 Radar chart saved as '{name}_persona_radar.png'")
    plt.show()

if __name__ == "__main__":
    run_survey()