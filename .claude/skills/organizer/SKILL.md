---
name: vault_organizer
description: Use this skill to process new files in the Needs_Action folder and update the Dashboard.
---

# Vault Organizer

## Instructions
1. **Scan**: Look for any `.md` files in the `Needs_Action` folder.
2. **Read**: Open the file and identify what it is (e.g., a notification about a new file in the Inbox).
3. **Update Dashboard**: 
   - Open `Dashboard.md`.
   - Add a bullet point under a "Recent Activity" heading with the filename and a summary.
4. **Cleanup**: Move the processed file from `Needs_Action` to the `Done` folder.
5. **Report**: Tell the user "Vault organized successfully."

## Examples
User: "Clean up my vault"
Claude: [Uses vault_organizer to move files and update Dashboard.md]