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

class EECZTyrant(Peer):
    def post_init(self):
        print "post_init(): %s here!" % self.id
        self.dummy_state = dict()
        self.dummy_state["cake"] = "lie"
        self.gamma = 0.1
        self.alpha = 0.2
        self.download_rates = {}
        self.upload_rates = {}
        self.streak = {}
        self.r = 3
        self.opt_thresh = self.up_bw/4
    
    def requests(self, peers, history):
        """
        peers: available info about the peers (who has what pieces)
        history: what's happened so far as far as this peer can see

        returns: a list of Request() objects

        This will be called after update_pieces() with the most recent state.
        """
        needed = lambda i: self.pieces[i] < self.conf.blocks_per_piece
        needed_pieces = filter(needed, range(len(self.pieces)))
        np_set = set(needed_pieces)  # sets support fast intersection ops.

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
        pieces_by_rarity = sorted(avail_count.items(), key=operator.itemgetter(1))

        # start requesting pieces, weighted by rarity
        requests = []
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

        # req_received = set()
        # for req in requests:
        #     req_received.add(req.requester_id)

        # update rates
        lastround_dl = []
        tworounds_ul = []
        try:
            lastround_dl = history.downloads[-1]
            tworounds_ul = history.uploads[-2]
        except IndexError:
            pass

        all_peers = set()
        for p in peers:
            if p.id not in self.upload_rates:
                self.upload_rates[p.id] = 1.
            if p.id not in self.download_rates:
                self.download_rates[p.id] = 0.
            all_peers.add(p.id)

        peers_unchoked = set()
        # update accordingly for peers who did unchoke me
        temp_rates = {}
        for dl in lastround_dl:
            # id of peer who I downloaded from
            p = dl.from_id
            peers_unchoked.add(p)
            if p in temp_rates:
                temp_rates[p] += dl.blocks 
            else:
                temp_rates[p] = dl.blocks

        # create set of peers uploaded to 2 rounds ago
        peers_uploaded_to = set()
        for ul in tworounds_ul:
            peers_uploaded_to.add(ul.to_id)
            
        for p in temp_rates:
            # update download rates
            self.download_rates[p] = temp_rates[p]

            # update upload rates
            if p in self.streak:
                self.streak[p]["length"] = self.streak[p]["length"] + 1 if self.streak[p]["l_round"] == history.last_round() else 1
                self.streak[p]["l_round"] = history.current_round()
                if self.streak[p]["length"] >= self.r:
                    self.upload_rates[p] *= (1. - self.gamma)
            else:
                self.streak[p] = {"l_round": history.current_round(), "length": 1}

        peers_not_unchoked = all_peers - peers_unchoked
        for p in peers_not_unchoked.intersection(peers_uploaded_to):
            # check two rounds ago
            self.upload_rates[p] *= (1. + self.alpha)

        # store all ratios of download:upload
        rates = {}
        for p in all_peers:
            if self.download_rates[p] != 0:
                rates[p] = self.download_rates[p]/self.upload_rates[p]
        peers_by_rates = sorted(rates.items(), key=operator.itemgetter(1), reverse=True)
        print "*******RATES**********"
        print rates
        print "*****************"

        total_upload = 0
        uploads = []
        uploaded_to = set()
        for p, _ in peers_by_rates:
            total_upload += int(self.upload_rates[p])
            if total_upload <= self.up_bw:
                uploads.append(Upload(self.id, p, int(self.upload_rates[p])))
                uploaded_to.add(p)
            else:
                total_upload -= int(self.upload_rates[p])
                break
        print "*******UPLOADS**********"
        print self.upload_rates
        print "*****************"
        print "******DOwnloADS***********"
        print self.download_rates
        print "*****************"

        upload_left = all_peers - uploaded_to
        while self.up_bw - total_upload > self.opt_thresh and len(upload_left) > 0:
            p = random.sample(upload_left, 1)[0]
            upload_left.remove(p)
            uploads.append(Upload(self.id, p, self.opt_thresh))
            total_upload += self.opt_thresh
        
        print "*****************"
        print uploads
        print "*****************"
        return uploads
