jQuery(document).ready(function(){
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
});