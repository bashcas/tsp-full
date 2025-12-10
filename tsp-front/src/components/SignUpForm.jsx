import '../styles/Form.css'
import { useContext, useEffect, useRef } from 'react'
import { GlobalContext } from '../context/GlobalContext'
import { Message } from './Message'
import { post } from '../utilities/post'

const SignUpForm = () => {
  const {
    endpoint,
    url_paths,
    message,
    setMessage,
    local,
    saveItem,
    setLoading,
  } = useContext(GlobalContext)
  const recaptchaRef = useRef(null)
  const recaptchaWidgetId = useRef(null)

  useEffect(() => {
    // Wait for reCAPTCHA script to load and execute
    const loadRecaptcha = () => {
      // Check if grecaptcha is available (could be grecaptcha or grecaptcha.enterprise)
      const grecaptcha = window.grecaptcha?.enterprise || window.grecaptcha

      if (grecaptcha && grecaptcha.ready && recaptchaRef.current) {
        grecaptcha.ready(() => {
          // reCAPTCHA is ready, now render it programmatically
          if (!recaptchaWidgetId.current && recaptchaRef.current) {
            try {
              // Try Enterprise API first, then fallback to standard
              if (window.grecaptcha?.enterprise?.render) {
                recaptchaWidgetId.current = window.grecaptcha.enterprise.render(
                  recaptchaRef.current,
                  {
                    sitekey: '6LfDJCYsAAAAAO-v3j513CxzW28ScSxN8WmcI-z0',
                    action: 'SIGNUP',
                  }
                )
              } else if (grecaptcha.render) {
                recaptchaWidgetId.current = grecaptcha.render(
                  recaptchaRef.current,
                  {
                    sitekey: '6LfDJCYsAAAAAO-v3j513CxzW28ScSxN8WmcI-z0',
                    action: 'SIGNUP',
                  }
                )
              }
            } catch (error) {
              console.error('Error rendering reCAPTCHA:', error)
            }
          }
        })
      } else if (!grecaptcha) {
        // Retry if script not loaded yet
        setTimeout(loadRecaptcha, 100)
      }
    }

    loadRecaptcha()

    // Cleanup function
    return () => {
      if (recaptchaWidgetId.current !== null) {
        const grecaptcha = window.grecaptcha?.enterprise || window.grecaptcha
        if (grecaptcha && grecaptcha.reset) {
          grecaptcha.reset(recaptchaWidgetId.current)
        }
      }
    }
  }, [])

  const onSubmitSignUp = async (e) => {
    setLoading(true)
    e.preventDefault()

    // Get reCAPTCHA token
    let recaptchaToken = ''
    const grecaptcha = window.grecaptcha?.enterprise || window.grecaptcha

    if (
      grecaptcha &&
      recaptchaWidgetId.current !== null &&
      grecaptcha.getResponse
    ) {
      recaptchaToken = grecaptcha.getResponse(recaptchaWidgetId.current)
    } else if (recaptchaRef.current) {
      // Fallback: try to find the hidden textarea
      const responseElement = recaptchaRef.current.querySelector(
        'textarea[name="g-recaptcha-response"]'
      )
      if (responseElement) {
        recaptchaToken = responseElement.value
      } else {
        // Alternative: try to find it in the form
        const formElement = e.target
        const textarea = formElement.querySelector(
          'textarea[name="g-recaptcha-response"]'
        )
        if (textarea) {
          recaptchaToken = textarea.value
        }
      }
    }

    if (!recaptchaToken) {
      setMessage('Please complete the reCAPTCHA verification')
      setTimeout(() => {
        setMessage(null)
      }, 3000)
      setLoading(false)
      return
    }

    const form = new FormData(e.target)
    const data = {}
    form.forEach((value, key) => {
      data[key] = value
    })

    // Add reCAPTCHA token to form data
    data.recaptcha_token = recaptchaToken

    if (data.password !== data.repassword) {
      setMessage('passwords does not match')
      setTimeout(() => {
        setMessage(null)
      }, 3000)
      setLoading(false)
      return
    }

    const { status, response } = await post(endpoint + url_paths.signup, data)

    if (status !== 200) {
      setMessage(response.message)
      setTimeout(() => {
        setMessage(null)
      }, 3000)
    } else {
      const newLocal = { ...local, ...{ token: response.token } }
      saveItem(newLocal)
    }
    setLoading(false)
  }

  return (
    <div className="signup-form">
      <p className="form__title">Create your account</p>

      {message && <Message message={message} />}

      <form action="" onSubmit={onSubmitSignUp}>
        <div className="form__input">
          <label htmlFor="name">full name</label>
          <input
            type="text"
            name="name"
            id="name"
            required
            placeholder="Ivan Castellanos"
          />
        </div>
        <div className="form__input">
          <label htmlFor="username">username</label>
          <input
            type="text"
            name="username"
            id="username"
            required
            placeholder="necastellanosb"
          />
        </div>
        <div className="form__input">
          <label htmlFor="email">email</label>
          <input
            type="email"
            name="email"
            id="email"
            required
            placeholder="user@mail.com"
          />
        </div>
        <div className="form__input">
          <label htmlFor="password">password</label>
          <input
            type="password"
            name="password"
            id="password"
            required
            placeholder="type a strong password"
          />
        </div>
        <div className="form__input">
          <label htmlFor="repassword">confirm password</label>
          <input
            type="password"
            name="repassword"
            id="repassword"
            required
            placeholder="type again strong password"
          />
        </div>

        <div className="form__input">
          <div ref={recaptchaRef}></div>
        </div>

        <div className="form__button">
          <button className="button" type="submit">
            register
          </button>
        </div>
      </form>
    </div>
  )
}

export { SignUpForm }
