jQuery(document).ready(function(){
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
                console.debug("Success sending chat message");
            }
        });
        return false;
    });
});