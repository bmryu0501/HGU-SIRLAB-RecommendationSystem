from recommender_system import Pibo_recommender
import argparse
import socket
import threading
import time

# TODO: make DB update condition

def handle_client(client_socket: socket.socket):
    '''
    Handle client

    Parameters
    ----------
    client_socket : socket object
        socket object for client

    Returns
    -------
    None.


    incoming message format:
    {
        [0] command
        [1] user_id

        if command == 'recommend':
            None.
        elif command == 'update':
            [2] category
            if category == 'achievement':
                [3] category_id
                [4] task_id
                [5] parent_score
                [6] expert_score
            elif category == 'engagement':
                [3] category_id
                [4] task_id
                [5] engagment_score
                [6] engagement_level
    }

    outgoing message format:
    {
        if command == 'recommend':
            [0] TID recommend based on achievement
            [1] TID recommend based on engagement
        elif command == 'update':
            [0] success or fail #TODO : success or fail implement in Pibo_recommender

    '''
    user = client_socket.recv(65535)
    message = user.decode()

    # message parsing
    message = message.split(' ')
    print("message:", message)
    command = message[0]
    print("command:", command)
    user_id = int(message[1])
    print("user_id:", user_id)

    ### command execution ###
    # recommend task to user
    if command == 'recommend':
        recommender = Pibo_recommender.recommend_SVD()
        recommended_tasks = []
        recommended_tasks.append(recommender.recommend_achievement(user_id))
        recommended_tasks.append(recommender.recommend_engagement(user_id))
        

        print("recommend_task:", recommended_tasks)
        message = str(recommended_tasks[0]) + ' ' + str(recommended_tasks[1])
        client_socket.sendall(message.encode())
        print("------------------------------------")
        time.sleep(20)
        client_socket.close()

    # update achievement evaluation
    elif command == 'update':
        if message[2] == 'achievement':
            category_id = int(message[3])
            task_id = int(message[4])
            parent_score = int(message[5])
            expert_score = int(message[6])
            
            try:
                recommender = Pibo_recommender.recommend_SVD()
                recommender.update_achievement(user_id, category_id, task_id, parent_score, expert_score)
                message = 'success'
            except:
                message = 'fail'
            client_socket.sendall(message.encode())
            time.sleep(20)
            client_socket.close()

        elif message[2] == 'engagement':
            category_id = int(message[3])
            task_id = int(message[4])
            engagement_score = int(message[5])
            engagement_level = int(message[6])
            try:
                recommender = Pibo_recommender.recommend_SVD()
                recommender.update_engagement(user_id, task_id, engagement_score, engagement_level)
                message = 'success'
            except:
                message = 'fail'
            client_socket.sendall(message.encode())
            time.sleep(20)
            client_socket.close()
        else:
            print("wrong message\n")
            message = "wrong message"
            client_socket.sendall(message.encode())
            time.sleep(20)
            client_socket.close()

    # if command is not recommend or update, close socket
    else:
        print("command is not recommend or update")
        client_socket.close()

def accept_func(host, port):
    global server_socket
    #IPv4 protocol, TCP type socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #to handle "Address already in use" error
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #bind host and port
    server_socket.bind((host, port))
    #server allows a maximum of 5 queued connections
    server_socket.listen(5)

    while True:
        try:
            # if client is connected, return new socket object and client's address
            client_socket, addr = server_socket.accept()            
        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            break

        # accept input with accept() function
        # and after that, handle client with handle_client function using new thread
        print("------------------------------------")
        print("Connected by", addr)
        client_handler = threading.Thread(
            target=handle_client,
            args=(client_socket,)
        )
        client_handler.daemon = True
        # print("client_handler.daemon:", client_handler.daemon)
        client_handler.start()
    



if __name__ == '__main__':
    """
    argparse = argparse.ArgumentParser(description="\nrecommender system\n-h host\n-p port\n-m message\n")
    argparse.add_argument('-h', help="host")
    argparse.add_argument('-p', help="port")
    argparse.add_argument('-m', help="message")

    args = argparse.parse_args()
    try:
        host = args.h
        port = int(args.p)
        message = args.m
    except:
        pass
    """

    host = "ec2-13-209-85-23.ap-northeast-2.compute.amazonaws.com"
    port = 8080


    #recommender = Pibo_recommender.recommend_SVD()
    #recommender.update_model_achievement()
    #recommender.update_model_engagement()
    
    accept_func(host, port)
    
    