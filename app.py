from flask import Flask, render_template, request, jsonify, send_file
import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import os
import io
import base64

app = Flask(__name__)

# Data storage (in production, use a proper database)
user_data = {}


def get_random_animals(count):
    animals = [
        "Lion",
        "Eagle",
        "Dolphin",
        "Wolf",
        "Elephant",
        "Giraffe",
        "Penguin",
        "Bear",
        "Fox",
        "Owl",
    ]
    return random.sample(animals, count)


def create_radar_chart(skills_data, interests_data, name):
    # Create figure with polar subplot (doubled size)
    fig, ax = plt.subplots(figsize=(20, 20), subplot_kw=dict(projection="polar"))

    # Number of variables
    categories = [item["animal"] for item in skills_data]
    N = len(categories)

    # Angles for each axis
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Complete the loop

    # Skills values (1-5 scale)
    skill_values = [item["skill"] for item in skills_data]
    skill_values += skill_values[:1]  # Complete the loop

    # Interest values (1-3 scale, map to 1-5 for display)
    interest_values = [
        item["interest"] * (5 / 3) for item in interests_data
    ]  # Map 1-3 to ~1.7-5
    interest_values += interest_values[:1]  # Complete the loop

    # Plot skills (red)
    ax.plot(
        angles, skill_values, "o-", linewidth=3, color="red", alpha=0.7, label="Skills"
    )
    ax.fill(angles, skill_values, alpha=0.25, color="red")

    # Plot interests (dashed green line)
    ax.plot(
        angles,
        interest_values,
        "s--",
        linewidth=3,
        color="green",
        alpha=0.7,
        label="Interests",
    )
    ax.fill(angles, interest_values, alpha=0.15, color="green")

    # Add labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=24)

    # Set y-axis limits
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1", "2", "3", "4", "5"], fontsize=20)

    # Add grid
    ax.grid(True, alpha=0.3)

    # Add legend
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=24)

    # Title
    plt.title(
        f"Skills vs Interests Radar Chart",
        size=32,
        weight="bold",
        pad=40,
    )

    plt.tight_layout()

    # Convert to base64 string for web display
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format="png", dpi=300, bbox_inches="tight")
    img_buffer.seek(0)
    img_str = base64.b64encode(img_buffer.read()).decode()
    plt.close()

    return img_str


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start_survey", methods=["POST"])
def start_survey():
    name = request.json.get("name", "").strip()
    if not name:
        return jsonify({"error": "Name is required"}), 400

    # Check for existing data
    if name in user_data:
        return jsonify(
            {
                "has_existing": True,
                "message": f"Found existing profile for {name}!",
                "existing_data": user_data[name],
            }
        )

    # Generate new random animals
    animals = get_random_animals(5)
    return jsonify({"has_existing": False, "animals": animals})


@app.route("/submit_survey", methods=["POST"])
def submit_survey():
    data = request.json
    name = data.get("name", "").strip()
    skills_data = data.get("skills", [])
    interests_data = data.get("interests", [])

    if not name or not skills_data or not interests_data:
        return jsonify({"error": "Missing required data"}), 400

    # Store user data
    user_data[name] = {"skills": skills_data, "interests": interests_data}

    # Create radar chart
    chart_data = create_radar_chart(skills_data, interests_data, name)

    return jsonify(
        {
            "success": True,
            "chart_data": chart_data,
            "message": f"Profile saved for {name}!",
        }
    )


@app.route("/generate_chart", methods=["POST"])
def generate_chart():
    skills_data = request.json.get("skills", [])
    interests_data = request.json.get("interests", [])

    if not skills_data or not interests_data:
        return jsonify({"error": "Missing data"}), 400

    # Create radar chart
    chart_data = create_radar_chart(skills_data, interests_data, "Live Preview")

    return jsonify({"success": True, "chart_data": chart_data})


@app.route("/load_profile", methods=["POST"])
def load_profile():
    name = request.json.get("name", "").strip()
    if not name or name not in user_data:
        return jsonify({"error": "Profile not found"}), 404

    data = user_data[name]
    chart_data = create_radar_chart(data["skills"], data["interests"], name)

    return jsonify(
        {
            "success": True,
            "chart_data": chart_data,
            "skills": data["skills"],
            "interests": data["interests"],
        }
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
