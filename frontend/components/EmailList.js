import { useState } from 'react'

const EmailList = ({ emails, loading, selectedEmail, onSelectEmail }) => {
  const [filter, setFilter] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')

  const filteredEmails = emails.filter(email => {
    // Apply filter
    if (filter === 'unprocessed' && email.is_processed) return false
    if (filter === 'processed' && !email.is_processed) return false
    if (filter === 'urgent' && email.urgency < 4) return false
    
    // Apply search
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase()
      return (
        email.subject.toLowerCase().includes(searchLower) ||
        email.sender.toLowerCase().includes(searchLower) ||
        email.body.toLowerCase().includes(searchLower)
      )
    }
    
    return true
  })

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <p>Loading emails...</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Filter and Search */}
      <div className="p-4 border-b">
        <div className="mb-3">
          <input
            type="text"
            placeholder="Search emails..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="flex space-x-2">
          <select
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="all">All Emails</option>
            <option value="unprocessed">Unprocessed</option>
            <option value="processed">Processed</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>
      </div>

      {/* Email List */}
      <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
        {filteredEmails.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            No emails found
          </div>
        ) : (
          filteredEmails.map(email => (
            <div
              key={email.id}
              className={`p-4 cursor-pointer hover:bg-gray-50 ${
                selectedEmail?.id === email.id ? 'bg-blue-50' : ''
              } ${!email.is_processed ? 'bg-yellow-50' : ''}`}
              onClick={() => onSelectEmail(email)}
            >
              <div className="flex justify-between items-start">
                <h3 className="text-sm font-medium truncate">{email.subject}</h3>
                <span className="text-xs text-gray-500">
                  {new Date(email.date).toLocaleDateString()}
                </span>
              </div>
              <p className="text-sm text-gray-500 truncate">{email.sender}</p>
              <div className="flex mt-2 space-x-2">
                <span className={`px-2 py-1 rounded text-xs ${
                  email.sentiment === 'positive' ? 'bg-green-100 text-green-800' :
                  email.sentiment === 'negative' ? 'bg-red-100 text-red-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {email.sentiment || 'neutral'}
                </span>
                <span className={`px-2 py-1 rounded text-xs ${
                  email.urgency > 3 ? 'bg-red-100 text-red-800' :
                  email.urgency > 1 ? 'bg-yellow-100 text-yellow-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  Urgency: {email.urgency || 1}
                </span>
                {email.category && (
                  <span className="px-2 py-1 rounded text-xs bg-blue-100 text-blue-800">
                    {email.category}
                  </span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default EmailList
