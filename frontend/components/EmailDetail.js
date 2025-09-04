import { useState } from 'react'

const EmailDetail = ({ email, onUpdate }) => {
  const [editedResponse, setEditedResponse] = useState('')
  const [sending, setSending] = useState(false)

  if (!email) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-500">Select an email to view details</p>
      </div>
    )
  }

  const handleSendResponse = async () => {
    try {
      setSending(true)
      
      // First update the response if edited
      if (editedResponse && editedResponse !== email.ai_response) {
        await fetch(`http://localhost:8000/emails/${email.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            ai_response: editedResponse
          })
        })
      }
      
      // Then send the response
      const response = await fetch(`http://localhost:8000/emails/${email.id}/send-response`, {
        method: 'POST'
      })
      
      if (response.ok) {
        alert('Response sent successfully!')
        onUpdate() // Refresh the email list
      } else {
        alert('Failed to send response')
      }
    } catch (error) {
      console.error('Error sending response:', error)
      alert('Error sending response')
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Email Header */}
      <div className="p-6 border-b">
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-lg font-medium">{email.subject}</h2>
            <p className="text-sm text-gray-500">
              From: {email.sender} • {new Date(email.date).toLocaleString()}
            </p>
          </div>
          <div className="flex space-x-2">
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
      </div>

      {/* Email Body */}
      <div className="p-6 border-b">
        <h3 className="text-sm font-medium text-gray-500 mb-2">Original Message</h3>
        <div className="bg-gray-50 p-4 rounded-md whitespace-pre-wrap">
          {email.body}
        </div>
      </div>

      {/* Extracted Information */}
      {email.extracted_info && Object.keys(email.extracted_info).length > 0 && (
        <div className="p-6 border-b">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Extracted Information</h3>
          <div className="grid grid-cols-2 gap-4">
            {Object.entries(email.extracted_info).map(([key, value]) => (
              Array.isArray(value) && value.length > 0 ? (
                <div key={key}>
                  <p className="text-sm font-medium capitalize">{key.replace('_', ' ')}</p>
                  <p className="text-sm text-gray-600">{value.join(', ')}</p>
                </div>
              ) : null
            ))}
          </div>
        </div>
      )}

      {/* AI Response */}
      <div className="p-6">
        <h3 className="text-sm font-medium text-gray-500 mb-2">AI Generated Response</h3>
        {email.ai_response ? (
          <>
            <textarea
              className="w-full h-40 p-3 border border-gray-300 rounded-md"
              value={editedResponse || email.ai_response}
              onChange={(e) => setEditedResponse(e.target.value)}
              placeholder="AI response will appear here..."
            />
            <div className="mt-4 flex justify-end">
              <button
                onClick={handleSendResponse}
                disabled={sending}
                className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md disabled:opacity-50"
              >
                {sending ? 'Sending...' : 'Send Response'}
              </button>
            </div>
          </>
        ) : (
          <p className="text-gray-500">No AI response generated yet. Processing may still be in progress.</p>
        )}
      </div>
    </div>
  )
}

export default EmailDetail
