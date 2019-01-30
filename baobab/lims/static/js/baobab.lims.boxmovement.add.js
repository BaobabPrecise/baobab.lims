function BaobabBoxMovementEditView() {

    var that = this;

    that.load = function () {
        var path = window.location.href.split('edit')[0] + 'get_boxmovement_creation_datetime';
        var title = $('#breadcrumbs-current').text();

        $.ajax({
            type: 'GET',
            dataType: 'json',
            url: path,
            data: {'title': title}
        }).done(function (data) {
            var creation_date = data['creation_date_time'];
            if (creation_date) {
                var final_creation_date = getDatePickerDateAndTime(creation_date);
                $('#DateCreated').val(final_creation_date);
            }
        })
    };

    function getDatePickerDateAndTime(plone_date){
        try{
            var new_date = new Date(plone_date);

            var gmt_format_date = getGMTFormatDate(plone_date);

            return gmt_format_date
        }
        catch(err){
            console.debug("Error: " + err.message);
            return plone_date
        }

    }

    function getGMTFormatDate(plone_date_string){

        var pieces = plone_date_string.split(/[-/ :]/);

        return [pieces[0], pieces[1], pieces[2]].join('-') + ' ' + [pieces[3], pieces[4]].join(':')
    }

}
