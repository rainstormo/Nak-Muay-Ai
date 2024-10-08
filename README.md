# Application Overview
This Muay Thai coaching application generates personalized workout plans. 

Users can input their training, equipment, day preferences and exercise-specific feedback. Based on this information, the app generates a weekly training plan tailored to the user. 

This is achieved through user-specific weightings of each filtered exercise which can be changed via direct user-feedback and a KNN model for group-matching. Exercises are filtered and balanced by preferences, musclegroups, equipment requirements and type to ensure each training day contains a consistent set of workouts and different types of workouts are spread in a given week.

The backend is built using Flask and MongoDB is used for the database. 

## Home Screen
![Home Screen](https://github.com/user-attachments/assets/3ff6497b-4696-4472-9a03-95bf04b5575a)  
*Description*: The Home Screen provides users with an overview of the main features.

## Registration
![Registration](https://github.com/user-attachments/assets/17c3da00-4741-41db-87a8-497166b660b9)  
*Description*: The Registration screen allows new users to create an account by providing their details.

## Login
![Login](https://github.com/user-attachments/assets/a532f530-8d02-438a-b955-e308f092ea76)  
*Description*: The Login screen enables returning users to access their accounts.

## Generating Plan
![Generating Plan](https://github.com/user-attachments/assets/7bde962e-400a-4b9c-aedd-9e6691e849ec)  
*Description*: This screen lets users generate a personalized training plan based on their preferences.

## Training Screen
![Training Screen](https://github.com/user-attachments/assets/1e3238fe-8f8e-4803-8e8c-ce79877219c6)  
*Description*: The Training screen provides a detailed view of the user's current workout day.


A literary review was done on the current use of AI in Muay Thai or similiar, it can be found here: [Artificial.Intelligence.for.Muay.Thai.-.Literature.Review.pdf](https://github.com/user-attachments/files/16882821/Artificial.Intelligence.for.Muay.Thai.-.Literature.Review.pdf)


Documentation covering the methods, results and discussions can be found here: [Machine learning for Muay Thai - Results.pdf](https://github.com/user-attachments/files/16882786/Machine.learning.for.Muay.Thai.-.Results.pdf)



