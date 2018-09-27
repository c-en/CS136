#!/usr/bin/python

# This is a dummy peer that just illustrates the available information your peers 
# have available.

# You'll want to copy this file to AgentNameXXX.py for various versions of XXX,
# probably get rid of the silly logging messages, and then add more logic.

import operator

import random
import logging

from messages import Upload, Request
from util import even_split
from peer import Peer

class EECZTourney(Peer):
    def post_init(self):
        print "post_init(): %s here!" % self.id
        self.needed = len(self.pieces)
        self.firstpieces = {}
    
    def requests(self, peers, history):
        """
        peers: available info about the peers (who has what pieces)
        history: what's happened so far as far as this peer can see

        returns: a list of Request() objects

        This will be called after update_pieces() with the most recent state.
        """
        requests = []
        needed = lambda i: self.pieces[i] < self.conf.blocks_per_piece
        needed_pieces = filter(needed, range(len(self.pieces)))
        np_set = set(needed_pieces)  # sets support fast intersection ops.
        self.needed = len(np_set)
        if self.needed == len(self.pieces):
            if len(self.firstpieces) == 0:
                for peer in peers:
                    starting_pieces = set(range(len(self.pieces)))
                    if len(peer.available_pieces) == self.needed:
                        self.firstpieces[peer] = random.sample(starting_pieces,1)[0]
                        starting_pieces.remove(self.firstpieces[peer])
            for peer in self.firstpieces:
                start_block = self.pieces[self.firstpieces[peer]]
                requests.append(Request(self.id, peer.id, self.firstpieces[peer], start_block))

        # sort needed pieces by rarity
        avail_count = {}
        isects = {}
        for peer in peers:
            av_set = set(peer.available_pieces)
            isects[peer] = av_set.intersection(np_set)
            for piece in isects[peer]:
                try:
                    avail_count[piece] += 1
                except:
                    avail_count[piece] = 1

        for piece in avail_count:
            avail_count[piece] /= float(1. + self.pieces[piece] / float(self.conf.blocks_per_piece))
        pieces_by_rarity = sorted(avail_count.items(), key=operator.itemgetter(1))

        # start requesting pieces, weighted by rarity
        for peer in peers:
            possible_requests = [(piece, 1./avail_count[piece]) for piece in isects[peer]]
            req_order = sorted([(r[0], random.random() * r[1]) for r in possible_requests], key=lambda x: x[1])
            to_request = req_order[-(self.max_requests):]
            for r in to_request[::-1]:
                start_block = self.pieces[r[0]]
                requests.append(Request(self.id, peer.id, r[0], start_block))

        return requests

    def uploads(self, requests, peers, history):
        """
        requests -- a list of the requests for this peer for this round
        peers -- available info about all the peers
        history -- history for all previous rounds

        returns: list of Upload objects.

        In each round, this will be called after requests().
        """

        # measure peers by bandwidth received over past round
        if self.needed == 0:
            return []

        req_received = set()
        for req in requests:
            req_received.add(req.requester_id)
        total_bandwidth_rec = {p: 0 for p in req_received}
        upload_allocation = {p: 0 for p in req_received}
        bw = 0
        pastround = []
        try:
            pastround.extend(history.downloads[-1])
        except IndexError:
            pass
        for dl in pastround:
            if dl.from_id in req_received:
                bw += dl.blocks
                total_bandwidth_rec[dl.from_id] += dl.blocks

        # allocate based on bandwidth received, with 10% saved for optimistic
        if bw == 0:
            for p in upload_allocation:
                upload_allocation[p] = float(self.up_bw) / len(req_received)
        else:
            optimistic_list = []
            for p in upload_allocation:
                if total_bandwidth_rec[p] == 0:
                    optimistic_list.append(p)
                else:
                    up = float(total_bandwidth_rec[p]) * self.up_bw / bw
                    upload_allocation[p] = up
            if len(optimistic_list) > 0:
                total_up = 0
                for p in upload_allocation:
                    upload_allocation[p] = int(0.9*upload_allocation[p])
                    total_up += upload_allocation[p]
                p = random.choice(optimistic_list)
                upload_allocation[p] = int(self.up_bw - total_up)

        uploads = [Upload(self.id, p, int(upload_allocation[p])) for p in upload_allocation]

        return uploads
