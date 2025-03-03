$('.plus-cart').click(function(){
    console.log('Button clicked')

    var id = $(this).attr('id')
    var quantity = this.parentNode.children[2] // елемент <span id="quantity"> 7 </span>
    //console.log(quantity)
    // AJAX (асинхронний (без перевантаження сторінки) JavaScript та XML) - запит на сервер. JQuery - спрощує роботу з JS; з AJAX.
    $.ajax({
         type: 'GET',
         url: '/pluscart',
         data: {
             cart_id: id
         },
// GET http://localhost:5000/pluscart?cart_id=123

         success: function(data){
             quantity.innerText = data.quantity

             document.getElementById(`quantity${id}`).innerText = data.quantity
             document.getElementById('amount_right').innerText = data.amount
             document.getElementById('total_amount').innerText = data.total
         }
    })
})


$('.minus-cart').click(function(){
    var id = $(this).attr('id')
    var quantity = this.parentNode.children[2]

    $.ajax({
        type: 'GET',
        url: '/minuscart',
        data: {
            cart_id: id
        },

        success: function(data){
            quantity.innerText = data.quantity

            document.getElementById(`quantity${id}`).innerText = data.quantity
            document.getElementById('amount_right').innerText = data.amount
            document.getElementById('total_amount').innerText = data.total
        }
    })
})


$('.remove-cart').click(function(){
     var id = $(this).attr('id').toString()
     var to_remove = this.parentNode.parentNode.parentNode.parentNode // div

    $.ajax({
        type: 'GET',
        url: '/removecart',
        data: {
            cart_id: id
        },

        success: function(data){
             document.getElementById('amount_right').innerText = data.amount
             document.getElementById('total_amount').innerText = data.total
             to_remove.remove() // delete div
        }
     })
})

function myFunction(id) {
    var dots = document.getElementById("dots"+id);
    var moreText = document.getElementById("more"+id);
    var btnText = document.getElementById("myBtn"+id);

    if (dots.style.display === "none") {
      dots.style.display = "inline";
      btnText.innerHTML = "Read more";
      moreText.style.display = "none";
    } else {
      dots.style.display = "none";
      btnText.innerHTML = "Read less";
      moreText.style.display = "inline";
    }
}
