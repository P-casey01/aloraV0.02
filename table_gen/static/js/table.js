document.addEventListener('DOMContentLoaded', () => {
    const mealPlanJson = document.querySelector('script[data-meal-plan]').dataset.mealPlan;
    const mealPlan = JSON.parse(mealPlanJson);
    const tbody = document.getElementById('mealPlanTable');

    for (const [day, dailyMeals] of Object.entries(mealPlan)) {
        for (const meal of dailyMeals) {
            const tr = document.createElement('tr');

            const dayCell = document.createElement('td');
            dayCell.textContent = day;
            tr.appendChild(dayCell);

            const mealNameCell = document.createElement('td');
            mealNameCell.textContent = meal['meal_name'];
            tr.appendChild(mealNameCell);

            const ingredientsCell = document.createElement('td');
            ingredientsCell.textContent = meal['ingredients'];
            tr.appendChild(ingredientsCell);

            const nutritionalContentCell = document.createElement('td');
            nutritionalContentCell.textContent = meal['nutritional_content'];
            tr.appendChild(nutritionalContentCell);

            const instructionsCell = document.createElement('td');
            instructionsCell.textContent = meal['instructions'];
            tr.appendChild(instructionsCell);

            tbody.appendChild(tr);
        }
    }
});

// Add your previousDay and nextDay functions here


function previousDay() {
    if (currentDay > 0) {
        currentDay--;
        displayDay(currentDay);
    }
}

function nextDay() {
    if (currentDay < Object.keys(mealPlan).length - 1) {
        currentDay++;
        displayDay(currentDay);
    }
}
document.getElementById('previousDay').addEventListener('click', previousDay);
document.getElementById('nextDay').addEventListener('click', nextDay);
