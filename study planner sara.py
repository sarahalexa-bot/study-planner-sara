"""
Smart Study Planner
--------------------
A console-based program that lets a student log, review and analyse
study sessions across different subjects over a semester.

Data is persisted to a text file (study_log.txt) so that sessions
logged in one run are still available the next time the program starts.

Author: <Your Name>
"""

import os

DATA_FILE = "study_log.txt"

DELIMITER = "|"


def load_sessions():
    """
    Load previously saved sessions from DATA_FILE.

    Returns a list of session dictionaries. If the file does not exist
    (e.g. the very first time the program is run), an empty list is
    returned instead of raising an error.
    """
    sessions = []


    if not os.path.exists(DATA_FILE):
        return sessions

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue  

                parts = line.split(DELIMITER)
                
                if len(parts) != 4:
                    continue  

                subject, topic, date, duration_str = parts
                try:
                    duration = float(duration_str)
                except ValueError:
                    continue  

                sessions.append({
                    "subject": subject,
                    "topic": topic,
                    "date": date,
                    "duration": duration
                })
    except OSError as error:

        print(f"Warning: could not read {DATA_FILE} ({error}). "
              f"Starting with an empty session list.")

    return sessions


def save_sessions(sessions):
    """
    Save every session in `sessions` to DATA_FILE, overwriting any
    previous contents. Called when the user chooses to save and exit.
    """
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            for session in sessions:
                line = DELIMITER.join([
                    session["subject"],
                    session["topic"],
                    session["date"],
                    str(session["duration"])
                ])
                file.write(line + "\n")
        print(f"Saved {len(sessions)} session(s) to {DATA_FILE}.")
    except OSError as error:
        print(f"Error: could not save sessions ({error}).")



def classify_session(duration):
    """
    Classify a session's duration (in minutes) as "Short", "Medium"
    or "Long".

    Short  : under 30 minutes
    Medium : 30 to 90 minutes (inclusive)
    Long   : over 90 minutes
    """
    if duration < 30:
        return "Short"
    elif duration <= 90:
        return "Medium"
    else:
        return "Long"


def get_valid_duration():
    """
    Repeatedly prompt the user for a session duration until a valid
    positive number is entered. Returns the duration as a float.
    """
    while True:
        raw_value = input("Duration (in minutes): ").strip()
        try:
            duration = float(raw_value)
            if duration <= 0:
                print("Duration must be a positive number. Please try again.")
                continue
            return duration
        except ValueError:
            print("Please enter a valid number for the duration.")


def add_session(sessions):
    """
    Prompt the user for the details of a new study session and append
    it to `sessions` as a dictionary.
    """
    print("\n--- Add a Study Session ---")
    subject = input("Subject: ").strip()
    topic = input("Topic covered: ").strip()
    date = input("Date / day label (e.g. 2026-09-01 or 'Monday'): ").strip()
    duration = get_valid_duration()

    session = {
        "subject": subject,
        "topic": topic,
        "date": date,
        "duration": duration
    }
    sessions.append(session)
    print(f"Session added: {subject} ({classify_session(duration)}, "
          f"{duration:.0f} min).")


def print_session_table(sessions):
    """
    Print a neatly formatted table of the given sessions, including
    each session's Short/Medium/Long classification.

    This helper is shared by view_sessions() and search_by_subject()
    so the table layout stays consistent everywhere sessions are shown.
    """
    header = f"{'Subject':<15}{'Topic':<20}{'Date':<15}{'Duration':<12}{'Type':<8}"
    print(header)
    print("-" * len(header))

    for session in sessions:
        classification = classify_session(session["duration"])
        row = (f"{session['subject']:<15}"
               f"{session['topic']:<20}"
               f"{session['date']:<15}"
               f"{session['duration']:<12.0f}"
               f"{classification:<8}")
        print(row)


def view_sessions(sessions):
    """Display every logged session in a formatted table."""
    print("\n--- All Study Sessions ---")
    if not sessions:
        print("No sessions have been logged yet.")
        return

    print_session_table(sessions)
    print(f"\nTotal sessions logged: {len(sessions)}")



def search_by_subject(sessions):
    """
    Ask the user for a subject name and display only the sessions
    matching that subject (case-insensitive), along with the total
    time spent on it.
    """
    print("\n--- Search Sessions by Subject ---")
    query = input("Enter subject to search for: ").strip()

   
    matches = [s for s in sessions if s["subject"].lower() == query.lower()]

    if not matches:
        print(f"No sessions found for subject '{query}'.")
        return

    print_session_table(matches)
    total_minutes = sum(s["duration"] for s in matches)
    print(f"\nTotal time spent on '{query}': {total_minutes:.0f} minutes "
          f"({total_minutes / 60:.2f} hours) across {len(matches)} session(s).")


def study_statistics(sessions):
    """
    Compute and display:
      - total hours studied overall
      - total hours studied per subject
      - the subject with the least total study time (weakest area)
      - the single longest session recorded
    """
    print("\n--- Study Statistics ---")
    if not sessions:
        print("No sessions have been logged yet, so no statistics are available.")
        return


    total_minutes = sum(s["duration"] for s in sessions)
    print(f"Total hours studied overall: {total_minutes / 60:.2f} hours")

  
    minutes_per_subject = {}
    for session in sessions:
        subject = session["subject"]
        minutes_per_subject[subject] = minutes_per_subject.get(subject, 0) + session["duration"]

    print("\nHours studied per subject:")
    for subject, minutes in minutes_per_subject.items():
        print(f"  {subject:<15}{minutes / 60:.2f} hours")


    weakest_subject = min(minutes_per_subject, key=minutes_per_subject.get)
    print(f"\nWeakest area (least total study time): {weakest_subject} "
          f"({minutes_per_subject[weakest_subject] / 60:.2f} hours)")

    longest_session = max(sessions, key=lambda s: s["duration"])
    print(f"\nLongest session recorded: {longest_session['subject']} - "
          f"{longest_session['topic']} on {longest_session['date']} "
          f"({longest_session['duration']:.0f} minutes, "
          f"{classify_session(longest_session['duration'])})")



def display_menu():
    """Print the main menu options."""
    print("\n===== Smart Study Planner =====")
    print("1. Add a study session")
    print("2. View all sessions")
    print("3. Search sessions by subject")
    print("4. View statistics")
    print("5. Save and exit")


def main():
    """
    Main program loop: loads existing sessions, repeatedly shows the
    menu and dispatches to the relevant function, and saves sessions
    to disk when the user exits.
    """
    sessions = load_sessions()
    print(f"Loaded {len(sessions)} existing session(s) from {DATA_FILE}.")

    while True:
        display_menu()
        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            add_session(sessions)
        elif choice == "2":
            view_sessions(sessions)
        elif choice == "3":
            search_by_subject(sessions)
        elif choice == "4":
            study_statistics(sessions)
        elif choice == "5":
            save_sessions(sessions)
            print("Goodbye - happy studying!")
            break
        else:
          
            print("Invalid choice. Please enter a number from 1 to 5.")


if __name__ == "__main__":
    main()
