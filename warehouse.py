#  Copyright (c) 2020, Will Traweek, All Rights Reserved.

from exceptions import *
from truck import Truck
from box import Box
from sortedcontainers import SortedList
import json


class Warehouse:
    """A warehouse stores boxes for shipping.  It can read in manifests and export them.  It also has a list of
    trucks assigned to it.  The largest part of the warehouse's job, though, is preparing said trucks for shipping.
    This is where the Knapsack algorithm comes into play.

    Attributes:
        trucks: A set of trucks available for the warehouse to use
        boxes: A dictionary containing all of the possible boxes and their quantities
        capacity: total capacity of all the trucks available
        value: total value of all of the boxes in the warehouse -- does not count the value inside the trucks
    """

    def __init__(self):
        self.trucks = SortedList()
        self.boxes = {}
        self.capacity = 0
        self.value = 0

    def __init__(self, input_file_path):
        self.trucks = SortedList()
        self.boxes = {}
        self.capacity = 0
        self.value = 0
        self.import_boxes(input_file_path)

    def import_boxes(self, input_file_path):
        """reads in boxes from a file and adds them to the dictionary"""
        input_file = open(input_file_path, "r")

        for line in input_file.readlines():
            name, weight, price = line.split(",")

            # prevents the first line from being read in
            if name == "name":
                continue

            self.add_box(Box(name, int(weight), int(price)))

    def to_json(self):
        """returns the items in the trucks and self.boxes in json"""
        output = {}
        trucks = {}
        boxes = {}

        warehouse = {
            "value": self.value,
            "total truck capacity": self.capacity,
            "trucks in fleet": len(self.trucks),
            "boxes in storage": len(self.boxes)
        }
        output["Warehouse"] = warehouse

        # list all boxes currently in trucks and the capacity of those trucks
        for i in range(len(self.trucks)):
            truck = {}

            truck["value"] = self.trucks[i].value
            truck["weight"] = self.trucks[i].weight
            truck["capacity"] = self.trucks[i].capacity
            truck["boxes"] = self.trucks[i].to_dict()

            trucks[f"Truck {i}"] = truck

        output["Truck Fleet"] = trucks

        # List all boxes still in floor storage
        for key, value in self.boxes.items():
            temp = {}
            temp["weight"] = key.weight
            temp["price"] = key.price
            temp["quantity"] = value

            boxes[key.name] = temp

        output["Boxes"] = boxes

        return json.dumps(output, indent=4)

    def add_truck(self, capacity):
        """Creates a new truck and adds it to the list"""
        self.trucks.add(Truck(capacity))
        self.capacity += capacity

    def add_truck(self, truck):
        """Adds a new truck to the list of trucks"""
        self.trucks.add(truck)
        self.capacity += truck.capacity

    def add_box(self, box):
        """add the passed box to the warehouse"""
        if box in self.boxes:
            self.boxes[box] += 1
        else:
            self.boxes[box] = 1

        self.value += box.price

    def remove_box(self, box):
        """removes the passed box from the warehouse"""
        if box not in self.boxes:
            raise BoxRemovalError("Box not in warehouse", box)
        elif self.boxes[box] == 0:
            raise BoxRemovalError("No boxes of this type left in warehouse", box)

        self.value -= box.price
        self.boxes[box] -= 1

        # if the removed item was the final one of its type, remove it
        if self.boxes[box] == 0:
            self.boxes.pop(box)

    def load_box(self, box, truck):
        """loads boxes from the warehouse into the truck"""
        try:
            self.remove_box(box)
            truck.add_box(box)
        except BoxAdditionError:
            # sometimes it will be unable to add the box to the truck. Box needs to go back to the warehouse.
            self.add_box(box)
        except BoxRemovalError:
            # if the box isn't in the warehouse, then return
            return

    def unload_box(self, box, truck):
        """unloads boxes from the truck and loads them into the warehouse"""
        try:
            truck.remove_box(box)
            self.add_box(box)
        except BoxRemovalError:
            # if the box isn't in the truck, then return
            return

    def num_boxes(self):
        """Iterates through the quantities of boxes and returns the full count of boxes in """
        output = 0
        for value in self.boxes.values():
            output += value
        return output

    def to_list(self):
        """converts the dictionary of boxes to a list for easier interfacing with the dynamic programming solution"""
        output = []
        for key, value in self.boxes.items():
            for i in range(value):
                output.append(key)
        return output
