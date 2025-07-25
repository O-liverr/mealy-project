CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('customer', 'admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Caterers (
    caterer_id SERIAL PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

CREATE TABLE MealOptions (
    meal_option_id SERIAL PRIMARY KEY,
    caterer_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (caterer_id) REFERENCES Caterers(caterer_id) ON DELETE CASCADE
);

CREATE TABLE Menus (
    menu_id SERIAL PRIMARY KEY,
    caterer_id INT NOT NULL,
    menu_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (caterer_id) REFERENCES Caterers(caterer_id) ON DELETE CASCADE,
    UNIQUE (caterer_id, menu_date)
);

CREATE TABLE MenuMealOptions (
    menu_id INT NOT NULL,
    meal_option_id INT NOT NULL,
    PRIMARY KEY (menu_id, meal_option_id),
    FOREIGN KEY (menu_id) REFERENCES Menus(menu_id) ON DELETE CASCADE,
    FOREIGN KEY (meal_option_id) REFERENCES MealOptions(meal_option_id) ON DELETE CASCADE
);

CREATE TABLE Orders (
    order_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    menu_id INT NOT NULL,
    meal_option_id INT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'confirmed', 'cancelled')),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (menu_id) REFERENCES Menus(menu_id) ON DELETE CASCADE,
    FOREIGN KEY (meal_option_id) REFERENCES MealOptions(meal_option_id) ON DELETE CASCADE
);

CREATE TABLE Notifications (
    notification_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    menu_id INT NOT NULL,
    message TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (menu_id) REFERENCES Menus(menu_id) ON DELETE CASCADE
);
