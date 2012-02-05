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
            return "/api/events/" + this.get("event_key") + "/chat";
        },
        parse: function(response) {
            console.info("ASKED TO PARSE RESP : " + response);
            /*if (response["events"]) {
                this.startIndex = response["events"]["start-index"];
                this.maxResults = response["events"]["max-results"];
                this.totalResults = response["events"]["total-results"];
                var rawGames = response["events"]["items"];
                var modelGames = rawGames.map(function(gameJson) {
                    startDateFromJson = gameJson["start_date"];
                    modelGame = new Game({
                        home_team_name     : gameJson["home_team"]["title"],
                        home_team_location : gameJson["home_team"]["location"],
                        home_team_logo_url : gameJson["home_team"]["logo_url"],
                        home_team_score    : gameJson["home_team"]["score"],
                        away_team_name     : gameJson["away_team"]["title"],
                        away_team_location : gameJson["away_team"]["location"],
                        away_team_logo_url : gameJson["away_team"]["logo_url"],
                        away_team_score    : gameJson["away_team"]["score"],
                        key                : gameJson["key"],
                        cancelled          : gameJson["cancelled"],
                        completed          : gameJson["completed"],
                        start_date         : startDateFromJson.split()[0],
                        start_time         : startDateFromJson.split()[1]
                    });
                    return modelGame;
                });
                this.collection.reset(modelGames);
            }
            }*/
        }
    });

    window.ChatSubmit = Backbone.Model.extend({
        initialize: function(options) {
            console.info("INIT CALLED ON ChatWindow");
        }
    });

    window.ChatMessagesWrapperView = Backbone.View.extend({
        initialize: function(options) {
            console.info("INIT CALLED ON ChatMessagesWrapperView")

            _(this).bindAll('change');
            this.model.bind('change', this.change);

            this._collectionView = new ChatMessagesView({
                collection:           this.model.collection,
                childViewConstructor: options.childViewConstructor,
                el:                   options.el
            });
        },

        change: function(wrappedCollection) {
            console.info("CHANGE called on ChatMessagesWrapperView");
            //var unwrappedCollection  = wrappedCollection.get("events")["items"];
            //this.model.collection.reset(wrappedCollection);
        }
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
            
            this._childViews.push(childView);
 
            if (this._rendered) {
                $(this.el).append(childView.render().el);
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
                username  : "ME",
                content   : "TEBOOOOOOOOW!",
                timestamp : "1:23 PM" 
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
            
        },
        
        initialize: function() {
            console.info("INIT The Chat App!!!!");
            
            this._chatWindow = new ChatMessagesWrapperView({
                model : this.model.chatMessages,
                childViewConstructor : ChatMessageView,
                el : $('#chat_messages')
            });

            this.fetchInitialMessages();
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