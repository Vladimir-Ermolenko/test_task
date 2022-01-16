# class used for more convenient storage of data
class Photo:
    def __init__(self, id, sol, camera, picture):
        self.id = str(id)
        self.sol = str(sol)
        self.camera = camera
        self.picture = picture

    def __str__(self):
        return self.id

    def __repr__(self):
        return self.id
