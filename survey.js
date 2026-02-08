const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

const animals = ['Lion', 'Eagle', 'Dolphin', 'Wolf', 'Elephant', 'Giraffe', 'Penguin', 'Bear', 'Fox', 'Owl'];
const selectedAnimals = [];

function getRandomAnimals(count) {
  const shuffled = [...animals].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, count);
}

function askQuestion(question) {
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      resolve(answer);
    });
  });
}

function drawRadarChart(skills) {
  const animalNames = Object.keys(skills);
  const values = Object.values(skills);
  const numPoints = animalNames.length;
  
  // Chart dimensions
  const width = 40;
  const height = 20;
  const centerX = Math.floor(width / 2);
  const centerY = Math.floor(height / 2);
  const maxRadius = Math.min(centerX, centerY) - 2;
  
  // Create canvas
  const canvas = Array(height).fill(null).map(() => Array(width).fill(' '));
  
  // Draw grid circles
  for (let level = 1; level <= 5; level++) {
    const radius = (maxRadius / 5) * level;
    for (let angle = 0; angle < 360; angle += 10) {
      const rad = (angle * Math.PI) / 180;
      const x = Math.round(centerX + radius * Math.cos(rad));
      const y = Math.round(centerY + radius * Math.sin(rad));
      if (x >= 0 && x < width && y >= 0 && y < height) {
        canvas[y][x] = level === 5 ? '.' : '.';
      }
    }
  }
  
  // Draw axes and labels
  for (let i = 0; i < numPoints; i++) {
    const angle = (i * 2 * Math.PI) / numPoints - Math.PI / 2;
    const endX = Math.round(centerX + maxRadius * Math.cos(angle));
    const endY = Math.round(centerY + maxRadius * Math.sin(angle));
    
    // Draw axis line
    for (let r = 0; r <= maxRadius; r++) {
      const x = Math.round(centerX + r * Math.cos(angle));
      const y = Math.round(centerY + r * Math.sin(angle));
      if (x >= 0 && x < width && y >= 0 && y < height) {
        canvas[y][x] = canvas[y][x] === '.' ? '.' : '+';
      }
    }
    
    // Place labels
    const labelX = Math.round(centerX + (maxRadius + 2) * Math.cos(angle));
    const labelY = Math.round(centerY + (maxRadius + 2) * Math.sin(angle));
    const label = animalNames[i].padEnd(8);
    for (let j = 0; j < Math.min(label.length, width - labelX); j++) {
      if (labelX + j >= 0 && labelX + j < width && labelY >= 0 && labelY < height) {
        canvas[labelY][labelX + j] = label[j];
      }
    }
  }
  
  // Draw data polygon
  const dataPoints = [];
  for (let i = 0; i < numPoints; i++) {
    const angle = (i * 2 * Math.PI) / numPoints - Math.PI / 2;
    const radius = (values[i] / 5) * maxRadius;
    const x = Math.round(centerX + radius * Math.cos(angle));
    const y = Math.round(centerY + radius * Math.sin(angle));
    dataPoints.push({ x, y });
  }
  
  // Connect data points
  for (let i = 0; i < numPoints; i++) {
    const start = dataPoints[i];
    const end = dataPoints[(i + 1) % numPoints];
    
    // Simple line drawing
    const steps = 10;
    for (let step = 0; step <= steps; step++) {
      const t = step / steps;
      const x = Math.round(start.x + t * (end.x - start.x));
      const y = Math.round(start.y + t * (end.y - start.y));
      if (x >= 0 && x < width && y >= 0 && y < height) {
        canvas[y][x] = '*';
      }
    }
    
    // Mark data points
    canvas[start.y][start.x] = '@';
  }
  
  // Print canvas
  for (const row of canvas) {
    console.log(row.join(''));
  }
  
  // Legend
  console.log('\nLegend: @ = data points, * = skill polygon, + = axes, . = grid');
}

async function runSurvey() {
  console.log('🎯 Persona Profile Survey\n');
  
  const name = await askQuestion('What is your name? ');
  console.log(`\nHello, ${name}! Please rate your skill level for each animal (1-5):\n`);
  
  const randomAnimals = getRandomAnimals(5);
  const skills = {};
  
  for (const animal of randomAnimals) {
    let rating;
    do {
      rating = await askQuestion(`${animal} skill (1=Low, 5=High): `);
      rating = parseInt(rating);
    } while (isNaN(rating) || rating < 1 || rating > 5);
    
    skills[animal] = rating;
  }
  
  console.log('\n📊 Your Persona Profile:');
  console.log(`Name: ${name}`);
  for (const [animal, skill] of Object.entries(skills)) {
    const bars = '█'.repeat(skill);
    console.log(`${animal}: ${skill}/5 ${bars}`);
  }
  
  console.log('\n🎯 Radar Chart:');
  drawRadarChart(skills);
  
  rl.close();
}

runSurvey().catch(console.error);