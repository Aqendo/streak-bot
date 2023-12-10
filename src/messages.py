def get_stats_text(
    name: str, all_days: int, highest: int, attempt: int, current: int
) -> str:
    return f"""Hey {name}, these are your stats.

📅 You went {all_days} days without relapsing
⚡️ Your highest streak is {highest} days
💂 This is your {attempt} attempt
🔥 Your current streak is {current} days long
"""


def get_help_message() -> str:
    return """/streak - 🍀 start a new streak
/relapse - 🗑 relapse a streak
/enableScoreboard - ✅  make your account show up on the scoreboard
/setStreak <daysCount> - ⚙️ set a custom streak
/stats - 📊 display some statistics 
/check <id/username> - 🔧  deletes account from scoreboard if it's been deleted
/deleteAllDataAboutMe - 🗑 Delete all data about yourself
/removeFromLeaderboard <id/username> - 🗑 Remove user from leaderboard of this group (admin-only!)
/returnToLeaderboard <id/username> - 🗑 Return user to leaderboard of this group, if it's banned (admin-only!)
"""


def get_relapse_message(days: str, name: str) -> str:
    return f"""🗑 Sad to see your streak of {days} days go down the drain.

I started a new streak for you.

🍀 Good luck, {name}, you will need it.

👉🏻 Check the <a href='https://easypeasymethod.org/'>easypeasy</a> method, it might help you."""
