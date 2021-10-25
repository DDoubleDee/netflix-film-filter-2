function quicksearch() {
    var input, ul, li, a, i, txtValue;
    input = document.getElementById('quicksearch').value.toUpperCase();
    ul = document.getElementById('titles');
    li = document.getElementsByTagName('li');
    ul.style.display = '';
    for(i=0;i<li.length;i++) {
        a = li[i].getElementsByTagName('a')[0];
        txtValue = a.textContent || a.innerText;
        if(txtValue.toUpperCase().indexOf(input)>-1){
            li.style.display = '';
        } else {
            li.style.display = 'none';
        }
    }
}