# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import torch
import logging
import torch.nn as nn
from seq2seq.nn.encoder_rnn import EncoderRNN
from seq2seq.nn.decoder_rnn_attention import DecoderRNNAttention
from seq2seq.models.tagger import Tagger
from seq2seq.utils import PAD_TOKEN, UNK_TOKEN

use_cuda = torch.cuda.is_available()
logger = logging.getLogger(__name__)


class BaseModel(nn.Module):
    """
    Base model
    Has support for taggers on source and target side, regardless of the chosen enc/dec
    """

    def __init__(self, n_words_src=0, n_words_trg=0, dim=0, emb_dim=0,
                 n_enc_layers=1, n_dec_layers=1,
                 dropout=0., bidirectional=True,
                 emb_dim_tags=0, n_tags_src=0, n_tags_trg=0, predict_src_tags=False, predict_trg_tags=False,
                 pass_hidden_state=True, vocab_src=None, vocab_trg=None, vocab_tags_src=None, vocab_tags_trg=None,
                 rnn_type='gru'):

        super(BaseModel, self).__init__()

        self.n_enc_layers = n_enc_layers
        self.n_dec_layers = n_dec_layers
        self.dim = dim
        self.emb_dim = emb_dim
        self.emb_dim_tags = emb_dim_tags  # for factored input

        self.n_words_src = n_words_src
        self.n_words_trg = n_words_trg

        self.dropout = dropout
        self.predict_src_tags = predict_src_tags
        self.predict_trg_tags = predict_trg_tags

        self.vocab_src = vocab_src
        self.vocab_trg = vocab_trg
        self.vocab_tags_src = vocab_tags_src
        self.vocab_tags_trg = vocab_tags_trg

        self.rnn_type = rnn_type

        self.pass_hidden_state = pass_hidden_state  # TODO not implemented outside model1
        logger.warning("pass_hidden_state=%s" % pass_hidden_state)

        self.src_tagger = None
        self.trg_tagger = None

        self.src_pad_idx = vocab_src.stoi[PAD_TOKEN]
        self.src_unk_idx = vocab_src.stoi[UNK_TOKEN]
        self.trg_pad_idx = vocab_trg.stoi[PAD_TOKEN]
        self.trg_unk_idx = vocab_trg.stoi[UNK_TOKEN]

        self.criterion = nn.NLLLoss(reduce=False, size_average=False, ignore_index=self.trg_pad_idx)

        if predict_src_tags:
            self.src_tagger = Tagger(dim=2 * dim if bidirectional else dim, n_tags=n_tags_src)

        if predict_trg_tags:
            self.trg_tagger = Tagger(dim=dim, n_tags=n_tags_trg)

    def forward(self):
        raise NotImplementedError('needs to be overridden')
