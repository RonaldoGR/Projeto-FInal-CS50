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
      let location = document.getElementById('location').value
      if (!name) {
          window.alert("Must provide name!")
          return
      } else if (!email) {
          window.alert("Must provide e-mail!")
          return
      }
      else if (!birthday) {
          window.alert("Must provide birthdaydate!")
          return
      }  else if (!password || password != confirmation) {
          window.alert("Must provide password or password is not confirm!")
      }  else if (!location) {
          window.alert("Must provide location!")
          return
      } 

     
  
      try { 
        let response = await fetch('/register', {
            method:'POST',
            headers: {'Content-type': 'application/json'},
            body: JSON.stringify({ name: name, email: email, password: password, location: location, birthday: birthday })
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
