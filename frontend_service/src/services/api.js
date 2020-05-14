import axios from 'axios'

export default axios.create({
  baseURL: 'http://database_api:5000'
})
