function ExportTableView(){
    this.load = function(){
        alert('Arrived');
        $(".deleteExportLink a").click(function(){
            alert("Here");
            showConfirmationLink();
        })
    };

    function showConfirmationLink(){
        $(this).hide();
        $(this).closest('.deleteExportConfirmation').show();
    }
}