from collections import Counter
import matplotlib.pyplot as plt
import networkx as nx
import sys
import time
from TwitterAPI import TwitterAPI
consumer_key = 'xxxxxxxxxxxxxxxxx'
consumer_secret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxx'
access_token = 'xxxxxxxxxxxxxxxxxxxx'
access_token_secret = 'xxxxxxxxxxxxxxxxxxxx'


def get_twitter():
    """ 
    Construct an instance of TwitterAPI using the tokens you entered above.
    Returns:
      An instance of TwitterAPI.
    """
    return TwitterAPI(consumer_key, consumer_secret, access_token, access_token_secret)


def read_screen_names(filename):
    """
    Read a text file containing Twitter screen_names, one per line.

    Params:
        filename....Name of the file to read.
    Returns:
        A list of strings, one per screen_name, in the order they are listed
        in the file.

    """
    return [line.strip('\n').strip() for line in open(filename)]


def robust_request(twitter, resource, params, max_tries=5):
    """ 
    If a Twitter request fails, sleep for 15 minutes.
    Do this at most max_tries times before quitting.
    Args:
      twitter .... A TwitterAPI object.
      resource ... A resource string to request; e.g., "friends/ids"
      params ..... A parameter dict for the request, e.g., to specify
                   parameters like screen_name or count.
      max_tries .. The maximum number of tries to attempt.
    Returns:
      A TwitterResponse object, or None if failed.
    """
    for i in range(max_tries):
        request = twitter.request(resource, params)
        if request.status_code == 200:
            return request
        else:
            print('Got error %s \nsleeping for 15 minutes.' % request.text)
            sys.stderr.flush()
            time.sleep(61 * 15)


def get_users(twitter, screen_names):
    """
    Retrieve the Twitter user objects for each screen_name.
    Params:
        twitter........The TwitterAPI object.
        screen_names...A list of strings, one per screen_name
    Returns:
        A list of dicts, one per user, containing all the user information
        (e.g., screen_name, id, location, etc)

    """
    users = []
    r_request = robust_request(twitter, "users/lookup", {"screen_name": screen_names})
    for r in r_request:
        users.append(r)

    return users


def get_friends(twitter, screen_name):
    """ 
    Return a list of Twitter IDs for users that this person follows, up to 5000.

    Args:
        twitter.......The TwitterAPI object
        screen_name... a string of a Twitter screen name
    Returns:
        A list of ints, one per friend ID, sorted in ascending order.

    """
    r_request = robust_request(twitter, "friends/ids", {"screen_name": screen_name}).json()
    return sorted(r_request['ids'])


def add_all_friends(twitter, users):
    """ 
    Get the list of accounts each user follows.
    I.e., call the get_friends method for all 4 candidates.

    Store the result in each user's dict using a new key called 'friends'.

    Args:
        twitter...The TwitterAPI object.
        users.....The list of user dicts.
    Returns:
        Nothing

    """
    for u in users:
        u['friends'] = get_friends(twitter, u['screen_name'])


def print_num_friends(users):
    """
    Print the number of friends per candidate, sorted by candidate name.
    Args:
        users....The list of user dicts.
    Returns:
        Nothing
    """
    for u in users:
        print(u['screen_name'],len(u['friends']))


def count_friends(users):
    """ 
    Count how often each friend is followed.
    Args:
        users: a list of user dicts
    Returns:
        a Counter object mapping each friend to the number of candidates who follow them.

    """
    c_f = []
    for u in users:
        c_f = c_f + u['friends']
    return Counter(c_f)


def friend_overlap(users):
    """
    Compute the number of shared accounts followed by each pair of users.

    Args:
        users...The list of user dicts.

    Return: A list of tuples containing (user1, user2, N), where N is the
        number of accounts that both user1 and user2 follow.  

    """
    f_o = []
    for i in range(0,len(users)-1):
        for j in range(i+1,len(users)):
            com_f = Counter(users[i]['friends'] + users[j]['friends']).most_common()
            count = 0
            for k in range(0,len(com_f)):
                if com_f[k][1]==2:
                    count = count+1
            tup = (users[i]['screen_name'],users[j]['screen_name'],count)
            f_o.append(tup)

    sorted_val = sorted(f_o,key=lambda x: [-x[2], x[0], x[1]])
    return sorted_val


def followed_by_hillary_and_donald(users, twitter):
    """
    Find and return the screen_name of the one Twitter user followed by both Hillary
    Clinton and Donald Trump.
    Params:
        users.....The list of user dicts
        twitter...The Twitter API object
    Returns:
        A string containing the single Twitter screen_name of the user
        that is followed by both Hillary Clinton and Donald Trump.
    """
    for user in users:
        if user['screen_name'] == 'realDonaldTrump':
            fl1 = user['friends']
        if user['screen_name'] == 'HillaryClinton':
            fl2 = user['friends']
    fl = fl1 + fl2
    fid = Counter(fl).most_common()
    common_friends = []
    for id in fid:
        if id[1] == 2:
            r_request = robust_request(twitter, "users/lookup", {"user_id": id}).json()
            common_friends.append(r_request[0]['screen_name'])
        elif len(common_friends) == 0:
            common_friends.append("no common friend found")
            break
    
    return common_friends


def create_graph(users, friend_counts):
    """ Create a networkx undirected Graph, adding each candidate and friend
        as a node.

        Each candidate in the Graph will be represented by their screen_name,
        while each friend will be represented by their user id.

    Args:
      users...........The list of user dicts.
      friend_counts...The Counter dict mapping each friend to the number of candidates that follow them.
    Returns:
      A networkx Graph
    """
    G = nx.Graph()
    user = []
    for u in users:
        user.append(u['screen_name'])
        d[u['screen_name']]=u['screen_name']
    G.add_nodes_from(user)
    f_n = []

    for u in users:
        for friend in u['friends']:
            if friend_counts[friend]>= 2:
                f_n.append(friend)
                d[friend]=""
    G.add_nodes_from(f_n)

    for u in users:
        for friend in u['friends']:
            if friend in G.nodes():
                G.add_edge(u['screen_name'],friend,color='g')

    return G


def draw_network(graph, users, filename):
    """
    Draws the network to a file. 
    We have labelled the candidate nodes; the friend
    nodes have no labels (to reduce clutter).
    """
    plt.figure(figsize=(6,6))
    nx.draw_networkx(graph,with_labels=True,labels=d,alpha=0.3,node_size=30)
    #plt.show(graph)
    plt.savefig(filename)


def main():
    """ Main method """
    twitter = get_twitter()
    screen_names = read_screen_names('candidates.txt')
    print('Established Twitter connection.')
    print('Read screen names: %s' % screen_names)
    users = sorted(get_users(twitter, screen_names), key=lambda x: x['screen_name'])
    print('found %d users with screen_names %s' %
          (len(users), str([u['screen_name'] for u in users])))
    add_all_friends(twitter, users)
    print('Friends per candidate:')
    print_num_friends(users)
    friend_counts = count_friends(users)
    print('Most common friends:\n%s' % str(friend_counts.most_common(5)))
    print('Friend Overlap:\n%s' % str(friend_overlap(users)))
    print('User followed by Hillary and Donald: %s' % followed_by_hillary_and_donald(users, twitter))

    graph = create_graph(users, friend_counts)
    print('graph has %s nodes and %s edges' % (len(graph.nodes()), len(graph.edges())))
    draw_network(graph, users, 'network.png')
    print('network drawn to network.png')

if __name__ == '__main__':
    main()




