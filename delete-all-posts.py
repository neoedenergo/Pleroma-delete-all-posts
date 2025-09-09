def main():
    from time import sleep
    from json import loads
    from rich.progress import Progress, TextColumn, BarColumn, MofNCompleteColumn, TimeRemainingColumn, TimeElapsedColumn
    from requests import get, delete, post
    from os import system, name
    import urllib3

    # The python requests library has issues with verifying SSL certs sometimes (idk why) so in order to avoid
    # that problem I import urllib3 and disable the warnings, also I set verify=False on the API requests
    # If you want to make sure SSL verification is on then remove the disable_warnings line and remove the
    # verify=False part on every API request.
    urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

    # Function to clean terminal on Windows(nt) and others (unix)
    def clear():
        if name == 'nt':
            system('cls')
        else:
            system('clear')

    # Configuring variables, you can hardcode this if you dont wanna have to type it manually everytime.
    print("Enter full URL of your Mastodon or Pleroma server.\nExample: https://www.my-pleroma-server.bunnies\n\n")
    url = input("Full URL: ")
    user = input("Username: ")
    password = input("Password: ")
    clear()

    # Obtaining ID of user and number of total posts
    user_id_response = loads(get(url + f"/api/v1/accounts/lookup?acct={user}", auth=(user, password), verify=False).text)
    total_posts = int(user_id_response['statuses_count'])
    print(f"""User has {total_posts} posts.

    This program will now proceed to delete and unreblog all posts.

    It takes 1 second per post due to API rate limits.

    In case the program halts before deleting all posts, please execute it one more time.\n""")

    # Obtaining status in chunks of 40 and deleting them until there is no more.

    with Progress(TextColumn("[progress.description]{task.description}", style= "Green"), BarColumn(), MofNCompleteColumn(), TimeElapsedColumn(), TimeRemainingColumn()) as progress: # This is for the fancy progress bar using the module "rich"
        progress_bar_task = progress.add_task(description="Deleting all posts: ", total=total_posts)

        while not progress.finished: # Keep deleting posts while the progress bar hasnt finished
            # Obtaining latest 40 status (40 is the maximum the Mastodon API allows to request)
            latest_40_status_response = loads(get(url + "/api/v1/accounts/" + user_id_response["id"] + "/statuses?limit=40", auth=(user, password), verify=False).text)

            if latest_40_status_response == []: # If the response is empty it means there is no posts anymore
                print("""Received no posts on the last API call.\n
                User might have no more posts to delete.
                You can run the program again to make sure.
                Halting program.\n""")
                input("Press enter to exit...")
                quit()

            for status in latest_40_status_response:
                sleep(1) # Mastodon API blocks you if you do more than 1 request per second
                if status["reblogged"] is True: # reblogs count as posts but cant be deleted normally, they have to be unreblogged, also the id of the original post must used in the request
                    progress.console.print(post(url + f"/api/v1/statuses/{status["reblog"]["id"]}/unreblog", auth=(user, password), verify=False)) # printing the API response to notify the user if something goes wrong, a reponse of 200 means everything is working as expected.
                else: # non-reblog posts, normal posts by the user are deleted like this:
                    progress.console.print(delete(url + "/api/v1/statuses/" + status["id"], auth=(user, password), verify=False)) # printing the API response to notify the user if something goes wrong, a reponse of 200 means everything is working as expected.
                progress.update(progress_bar_task, advance=1) # advancing the progress bar by 1

        print("All posts have been deleted.")
        input("Press enter to exit...")

    
if __name__ == "__main__":
    main()
