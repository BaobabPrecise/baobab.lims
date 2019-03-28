function ExportTableView() {
    this.load = function () {
        $("a.deleteExportLink").live('click', function (e) {
            e.preventDefault();
            $(this).closest('.exportActionLinks').hide();
            $(this).parent().next('.deleteExportConfirmation').show();
        });
        $("a.cancelDeleteExport").live('click', function (e) {
            e.preventDefault();
            $(this).closest('.deleteExportConfirmation').hide();
            $(this).parent().prev('.exportActionLinks').show();
        });
        //AJAX call to delete and remove item on the display
        $("a.deleteExportCornfirmed").live('click', function (e) {
            e.preventDefault();
            var path = window.location.href.split('/export')[0] + '/removeexports';
            var doc_id = $(this).attr('id');
            $.ajax({
                type: 'POST',
                dataType: 'json',
                url: path,
                data: {
                    'id': doc_id
                }
            }).always(function (data) {
                var row_id = data['row_id']+'_tr';
                $('tr[id^="'+row_id+'"]').remove();
            })
        })
    };
}