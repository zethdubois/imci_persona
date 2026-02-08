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

# Data storage directory
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)


def get_safe_name(name):
    """Generate a safe filename base from the name"""
    safe_name = "".join(c for c in name if c.isalnum() or c in (" ", "-", "_")).rstrip()
    safe_name = safe_name.replace(" ", "_").lower()
    return safe_name


def get_profile_filename(name):
    """Generate a safe filename from the name"""
    safe_name = get_safe_name(name)
    return os.path.join(DATA_DIR, f"{safe_name}_persona.json")


def get_profile_image_filename(name):
    """Generate image filename for a profile"""
    safe_name = get_safe_name(name)
    return os.path.join(DATA_DIR, f"{safe_name}_profile.png")


def save_profile_to_file(name, skills_data, interests_data, image_data=None, tags=None):
    """Save profile to JSON file in data directory"""
    filename = get_profile_filename(name)
    profile_data = {"name": name, "skills": skills_data, "interests": interests_data, "tags": tags or []}
    with open(filename, "w") as f:
        json.dump(profile_data, f, indent=2)

    # Save image if provided
    if image_data:
        image_filename = get_profile_image_filename(name)
        # Decode base64 image data
        try:
            # Remove data URL prefix if present
            if "," in image_data:
                image_data = image_data.split(",")[1]
            image_bytes = base64.b64decode(image_data)
            with open(image_filename, "wb") as f:
                f.write(image_bytes)
        except Exception as e:
            print(f"Error saving image: {e}")

    return filename


def load_profile_from_file(name):
    """Load profile from JSON file"""
    filename = get_profile_filename(name)
    if os.path.exists(filename):
        with open(filename, "r") as f:
            data = json.load(f)
            # Check if there's an associated image
            image_filename = get_profile_image_filename(name)
            if os.path.exists(image_filename):
                with open(image_filename, "rb") as img_f:
                    image_data = base64.b64encode(img_f.read()).decode("utf-8")
                    data["image_data"] = f"data:image/png;base64,{image_data}"
            return data
    return None


def get_all_profiles():
    """Get all profiles from data directory"""
    profiles = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith("_persona.json"):
            filepath = os.path.join(DATA_DIR, filename)
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                    # Check if there's an associated image
                    name = data.get("name", "")
                    image_filename = get_profile_image_filename(name)
                    if os.path.exists(image_filename):
                        with open(image_filename, "rb") as img_f:
                            image_data = base64.b64encode(img_f.read()).decode("utf-8")
                            data["image_data"] = f"data:image/png;base64,{image_data}"
                    profiles.append(data)
            except (json.JSONDecodeError, IOError):
                continue
    return profiles


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
    try:
        # Create figure with polar subplot (doubled size)
        fig, ax = plt.subplots(figsize=(20, 20), subplot_kw=dict(projection="polar"))

        # Number of variables
        categories = [item["animal"] for item in skills_data]
        N = len(categories)
        
        if N == 0:
            raise ValueError("No categories found in skills data")

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
            linewidth=6,
            color="green",
            alpha=0.7,
            label="Interests",
        )
        ax.fill(angles, interest_values, alpha=0.0, color="green")

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
    except Exception as e:
        print(f"Error creating radar chart: {e}")
        plt.close()  # Make sure to close the plot even if there's an error
        raise e


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start_survey", methods=["POST"])
def start_survey():
    name = request.json.get("name", "").strip()
    if not name:
        return jsonify({"error": "Name is required"}), 400

    # Check for existing data in files
    existing_profile = load_profile_from_file(name)
    if existing_profile:
        return jsonify(
            {
                "has_existing": True,
                "message": f"Found existing profile for {name}!",
                "existing_data": {
                    "skills": existing_profile["skills"],
                    "interests": existing_profile["interests"],
                },
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
    image_data = data.get("image_data", None)

    if not name or not skills_data or not interests_data:
        return jsonify({"error": "Missing required data"}), 400

    # Save profile to file (with image if provided)
    tags_data = data.get("tags", [])
    filename = save_profile_to_file(name, skills_data, interests_data, image_data, tags_data)

    # Create radar chart
    chart_data = create_radar_chart(skills_data, interests_data, name)

    return jsonify(
        {
            "success": True,
            "chart_data": chart_data,
            "message": f"Profile saved for {name}!",
            "filename": filename,
        }
    )


@app.route("/generate_chart", methods=["POST"])
def generate_chart():
    try:
        skills_data = request.json.get("skills", [])
        interests_data = request.json.get("interests", [])

        if not skills_data or not interests_data:
            return jsonify({"error": "Missing data"}), 400

        # Additional validation
        if not all(isinstance(skill, dict) and "animal" in skill and "skill" in skill for skill in skills_data):
            return jsonify({"error": "Invalid skills data format"}), 400
            
        if not all(isinstance(interest, dict) and "animal" in interest and "interest" in interest for interest in interests_data):
            return jsonify({"error": "Invalid interests data format"}), 400

        # Create radar chart
        chart_data = create_radar_chart(skills_data, interests_data, "Live Preview")

        return jsonify({"success": True, "chart_data": chart_data})
    except Exception as e:
        print(f"Error in generate_chart: {e}")
        return jsonify({"error": f"Chart generation failed: {str(e)}"}), 500


@app.route("/get_collaborators", methods=["GET"])
def get_collaborators():
    """Get all collaborators from data directory"""
    profiles = get_all_profiles()
    return jsonify({"success": True, "collaborators": profiles})


@app.route("/load_profile", methods=["POST"])
def load_profile():
    name = request.json.get("name", "").strip()

    # Load from file
    data = load_profile_from_file(name)
    if not data:
        return jsonify({"error": "Profile not found"}), 404

    chart_data = create_radar_chart(data["skills"], data["interests"], name)

    return jsonify(
        {
            "success": True,
            "chart_data": chart_data,
            "skills": data["skills"],
            "interests": data["interests"],
            "image_data": data.get("image_data", None),
        }
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
