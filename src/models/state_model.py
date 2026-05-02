class TravelState:
    def __init__(self, destination, days, interests=None, trip_pace=None, transport_preference=None):
        self.destination = destination
        self.days = days
        self.interests = interests or []
        self.trip_pace = trip_pace
        self.transport_preference = transport_preference

        self.places = []
        self.activities = []

        self.hotels = []

        self.recommendations = []
    
        