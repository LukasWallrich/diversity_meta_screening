on run argv
    set varSubject to item 1 of argv
    set varContent to item 2 of argv
    set shouldSend to item 3 of argv
    set recipientDetails to items 4 through end of argv

    tell application "Microsoft Outlook"
        set newMail to make new outgoing message with properties {subject:varSubject, content:varContent}

        repeat with i from 1 to (count recipientDetails) by 2
            set varName to item i of recipientDetails
            set varEmail to item (i + 1) of recipientDetails
            make new recipient at newMail with properties {email address:{name:varName, address:varEmail}}
        end repeat

        if shouldSend is "true" then
            tell newMail to send
        end if
    end tell
end run
