# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
# pylint: disable=W0613,C0103,R0201,W0622
#
# Copyright (c) 2014, Arista Networks, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
#   Neither the name of Arista Networks nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ARISTA NETWORKS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
import logging

import webob
import webob.dec
import webob.exc

import routes
import routes.middleware

from ztpserver.serializers import Serializer
from ztpserver.constants import *

log = logging.getLogger(__name__)

class Controller(object):

    def __init__(self):
        self.serializer = Serializer()

    def index(self, request, **kwargs):
        return webob.exc.HTTPNoContent()

    def create(self, request, **kwargs):
        return webob.exc.HTTPNoContent()

    def new(self, request, **kwargs):
        return webob.exc.HTTPNoContent()

    def show(self, request, id, **kwargs):
        return webob.exc.HTTPNoContent()

    def update(self, request, id, **kwargs):
        return webob.exc.HTTPNoContent()

    def delete(self, request, id, **kwargs):
        return webob.exc.HTTPNoContent()

    def edit(self, request, id, **kwargs):
        return webob.exc.HTTPNoContent()

    def serialize(self, data, content_type=CONTENT_TYPE_HTML, **kwargs):
        return self.serializer.serialize(data, content_type, **kwargs)

    def deserialize(self, data, content_type=CONTENT_TYPE_HTML, **kwargs):
        return self.serializer.deserialize(data, content_type, **kwargs)

    def response(self, **kwargs):
        return webob.Response(**kwargs)

    @webob.dec.wsgify
    def __call__(self, request):
        action = request.urlvars['action']

        try:
            method = getattr(self, action)    #pylint: disable=R0921
            result = method(request, **request.urlvars)

        except Exception as e:
            log.exception(e)
            raise webob.exc.HTTPInternalServerError()

        if result is None:
            result = webob.exc.HTTPNoContent()

        elif isinstance(result, dict):
            # serialize body based on response content type
            if 'body' in result:
                content_type = result.get('content_type')
                result['body'] = self.serialize(result['body'], content_type)

            result.setdefault('status', 200)
            result.setdefault('content_type', CONTENT_TYPE_HTML)

            result = self.response(**result)   #pylint: disable=W0142

        #FIXME we should only return Response not FileApp
        elif not isinstance(result, webob.Response) and \
             not isinstance(result, webob.static.FileApp):
            result = webob.exc.HTTPInternalServerError()

        return result

class Router(object):

    def __init__(self, mapper):
        self.map = mapper
        self.router = routes.middleware.RoutesMiddleware(self.dispatch,
                                                         self.map)

    @webob.dec.wsgify
    def __call__(self, request):
        return self.router

    @webob.dec.wsgify
    def dispatch(self, request):
        try:
            return request.urlvars['controller']
        except KeyError:
            return webob.exc.HTTPNotFound()



