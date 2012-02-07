// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){
    window.ChatMessage = Backbone.Model.extend({
        validate: function(attrs) {
            console.info("VALIDATING ChatMessage : " + attrs);
        }
    });

    window.CollectionChatMessages = Backbone.Collection.extend({
        model: ChatMessage,
    });

    /**
     * Fetch called by a UI action - just use Backbone's
     * It will fire a change event if server state different from internal
     */
    window.PaginatedChatMessagesWrapper = Backbone.Model.extend({
        initialize: function(options) {
            console.info("INIT CALLED ON PaginatedChatMessagesWrapper");
            this.collection = new CollectionChatMessages([]);
        },
        url: function() {
            return "/api/events/" + window.event_key + "/chat";
        },
        parse: function(response) {
            if (response["messages"]) {
                this.startIndex = response["messages"]["start-index"];
                this.maxResults = response["messages"]["max-results"];
                this.totalResults = response["messages"]["total-results"];
                var rawMessages = response["messages"]["items"];
                var modelMessages = rawMessages.map(function(messageJson) {
                    modelMessage = new ChatMessage({
                        author    : messageJson["author_name"],
                        content   : messageJson["content"],
                        timestamp : messageJson["created_nice"]
                    });
                    return modelMessage;
                });
                this.collection.reset(modelMessages);
            }
        },
        add: function(chatMessage) {
            this.collection.add(new ChatMessage(chatMessage));
        }
    });

    window.ChatSubmit = Backbone.Model.extend({
        initialize: function(options) {
            console.info("INIT CALLED ON ChatSubmit");
        },
        url: function() {
            return "/api/events/" + window.event_key + "/chat";
        }
    });

    window.ChatSubmitView = Backbone.View.extend({
        initialize: function(options) {
            console.info("INIT CALLED ON ChatSubmitView");
        }
    });

    window.ChatMessagesWrapperView = Backbone.View.extend({
        initialize: function(options) {
            console.info("INIT CALLED ON ChatMessagesWrapperView")

            this._collectionView = new ChatMessagesView({
                collection:           this.model.collection,
                childViewConstructor: options.childViewConstructor,
                el:                   options.el
            });
        },
    });

    window.ChatMessagesView = Backbone.View.extend({
        initialize : function(options) {
            console.info("INIT CALLED ON ChatMessagesView");
            _(this).bindAll('add', 'reset', 'remove');
 
            if (!options.childViewConstructor) throw "no child view constructor provided";

            this._childViewConstructor = options.childViewConstructor;

            this._childViews = [];
 
            _(this.collection).each(this.add);
 
            this.collection.bind('add', this.add);
            this.collection.bind('remove', this.remove);
            this.collection.bind('reset', this.reset);
        },
 
        add : function(item) {
            var childView = new this._childViewConstructor({
                model :      item,
            });
            
            this._childViews.unshift(childView);
 
            if (this._rendered) {
                $(this.el).prepend(childView.render().el);
            }
        },
 
        remove : function(model) {
            var viewToRemove = _(this._childViews).select(function(cv) { 
                return cv.model === model; })[0];
            this._childViews = _(this._childViews).without(viewToRemove);
            
            if (this._rendered) $(viewToRemove.el).remove();
        },

        reset : function(newCollection) {
            this._childViews = [];
            var that = this;
            newCollection.each(function(item) {
                that.add(item);
            });
            this.render()
        },
 
        render : function() {
            var that = this;
            this._rendered = true;
 
            $(this.el).empty();
 
            _(this._childViews).each(function(childView) {
                $(that.el).append(childView.render().el);
            });
 
            return this;
        }
    });

    window.ChatMessageView = Backbone.View.extend({
        tagName: "div",
        className: "msg",
        template: _.template($('#msg-template').html()),

        render : function() {
            $(this.el).html(this.template({
                author    : this.model.get("author"),
                content   : this.model.get("content"),
                timestamp : this.model.get("timestamp")
            }));
            return this;
        }
    });

    // The Application
    // ---------------
    
    // Our overall **AppView** is the top-level piece of UI.
    window.AppView = Backbone.View.extend({
        
        // Instead of generating a new element, bind to the existing skeleton of
        // the App already present in the HTML.
        el: $("#allchat"),
        
        events: {
            "submit #chat_submit" : "submitMessage"
        },
        
        initialize: function() {
            console.info("INIT The Chat App!!!!");
            
            this._chatWindow = new ChatMessagesWrapperView({
                model : this.model.chatMessages,
                childViewConstructor : ChatMessageView,
                el : $('#chat_messages')
            });

            this._chatSubmitView = new ChatSubmitView({
                model : this.model.chatSubmit,
                el : $('#chat_submit')
            });

            this.fetchInitialMessages();
            this.openChannel();
            $('#chat_input').focus();
        },
        
        render: function() {
            console.info("RENDER AT TOPLEVEL (nothing to do)!!!!");
        },

        fetchInitialMessages: function() {
            var ajaxParams = {
                dataType: "json",
                data: {
                    "max-results": 50
                }
            };
            this.model.chatMessages.fetch(ajaxParams);
        },

        openChannel: function() {
            console.info("Opening the GAE Channel!!");
            var token = window.token;
            var channel = new goog.appengine.Channel(token);
            var chatMessageModel = this.model.chatMessages;
            var handler = {
                onopen: function() {
                    console.info("GAE Channel opened!");
                },
                onmessage: function(msg) {
                    jsonMsg = JSON.parse(msg.data);
                    chatMessageModel.add(jsonMsg);
                },
                onerror: function(e) {
                    console.info("Received channel error : " + JSON.stringify(e));
                },
                onclose: function() {
                    console.info("GAE Channel closed!");
                }
            };
            var socket = channel.open(handler);
        },
        
        submitMessage: function(submitEvent) {
            var newChatEvent = new ChatMessage({
                content : submitEvent.currentTarget[0].value
            });
            saveErrorHandler = function(e) {
                console.info("GOT ERROR : " + JSON.stringify(e));
                //Show modal popup sometime later
                alert("Unauthorized - log in!");
            };
            $('#chat_input').val("");
            this.model.chatSubmit.save(newChatEvent, { error : saveErrorHandler });
        }
    });

    // Finally, we kick things off by creating the **App**.
    window.App = new AppView({model: {'chatMessages' : new PaginatedChatMessagesWrapper,
                                      'chatSubmit'   : new ChatSubmit }});
});

/*jQuery(document).ready(function(){
    jQuery('input.newMsgContent').focus();

    jQuery('.newChatForm').submit( function() {
        $.ajax({
            url     : $(this).attr('action'),
            type    : $(this).attr('method'),
            dataType: 'html',
            data    : $(this).serialize(),
            error   : function() {
                console.debug("Failure sending new chat message");
            },
            success : function() {
                jQuery('input.newMsgContent').attr('value', '');
                jQuery('input.newMsgContent').focus();
                console.debug("Success sending chat message");
            }
        });
        return false;
    });

    jQuery('.spinner')
        .hide()  // hide it initially
        .ajaxStart(function() {
            $(this).show();
        })
        .ajaxStop(function() {
            $(this).hide();
        });
        });*/