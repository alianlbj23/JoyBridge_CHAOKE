import roslibpy

class RosPublisher:
    def __init__(self, client, topics_config):
        self.publishers = []
        for t in topics_config:
            self.publishers.append({
                'indices': t['indices'],
                'pub': roslibpy.Topic(client, t['name'], 'std_msgs/Float32MultiArray')
            })

    def send(self, vec):
        for item in self.publishers:
            data_part = [vec[i] for i in item['indices']]
            msg = {'layout': {'dim': [], 'data_offset': 0}, 'data': data_part}
            item['pub'].publish(roslibpy.Message(msg))

    def close(self):
        for item in self.publishers:
            item['pub'].unadvertise()
