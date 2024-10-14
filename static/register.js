document.addEventListener("DOMContentLoaded", function (){
  document.getElementById('register').onclick=function(event){
      event.preventDefault() 
      register()
  }
  

  async function register() {

      let name = document.getElementById('username').value
      let email = document.getElementById('email').value
      let birthday = document.getElementById('birthday').value
      let password = document.getElementById('password').value
      let confirmation = document.getElementById('confirmation').value
      let country = document.getElementById('country').value
      let state = document.getElementById('state').value
      let city = document.getElementById('city').value
      let street = document.getElementById('street').value
      let num = document.getElementById('num').value

      let full_adress = {
        country: country,
        state: state,
        city: city,
        street: street,
        number: num
        
      }  

      let full_adress_json = JSON.stringify(full_adress)
      console.log("Full Adress: ", full_adress)
      if (!name || !email || !birthday || !password || password !== confirmation || !country || !state || !city || !street || !num) {
        window.alert("Please fill out all fields correctlyt!")
        return
      }

 
      try { 
        let response = await fetch('/register', {
            method:'POST',
            headers: {'Content-type': 'application/json'},
            body: JSON.stringify({ name: name, email: email, password: password, full_adress: full_adress_json, birthday: birthday })
        })

        if (response.ok || response.status === 400) {
        
            let result = await response.json()
            console.log(result.status)
            
            if (result.exists === "username") {
                window.alert("Username already exists!")
            } else if (result.exists === "email") {
                window.alert("Email already exists!")
                return false
            } else {
                window.alert("User register sucescefull")
                window.location.href = result.redirect
             } 
            } else {
                 window.alert("Error. Try again.")
            }
      } catch (error) {
        console.log("Error:", error)
      }
     

return true
}

})
