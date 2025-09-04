import { useState, useEffect } from 'react'
import Head from 'next/head'
import EmailList from '../components/EmailList'
import EmailDetail from '../components/EmailDetail'
import Analytics from '../components/Analytics'
import KnowledgeBase from '../components/KnowledgeBase'

export default function Home() {
  const [activeTab, setActiveTab] = useState('emails')
  const [selectedEmail, setSelectedEmail] = useState(null)
  const [emails, setEmails] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    fetchEmails()
  }, [])

  const fetchEmails = async () => {
    try {
      const response = await fetch('http://localhost:8000/emails/')
      const data = await response.json()
      setEmails(data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching emails:', error)
      setLoading(false)
    }
  }

  const processEmails = async () => {
    try {
      setRefreshing(true)
      const response = await fetch('http://localhost:8000/fetch-emails/', {
        method: 'POST'
      })
      const result = await response.json()
      alert(result.message)
      fetchEmails() // Refresh the email list
    } catch (error) {
      console.error('Error processing emails:', error)
      alert('Error processing emails')
    } finally {
      setRefreshing(false)
    }
  }

  return (
    <div>
      <Head>
        <title>Email Support Automation</title>
        <meta name="description" content="Automated email support system" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gray-100">
        {/* Header */}
        <header className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex justify-between items-center">
              <h1 className="text-2xl font-bold text-gray-900">Email Support Automation</h1>
              <button
                onClick={processEmails}
                disabled={refreshing}
                className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md disabled:opacity-50"
              >
                {refreshing ? 'Processing...' : 'Fetch & Process Emails'}
              </button>
            </div>
          </div>
        </header>

        {/* Navigation Tabs */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {['emails', 'analytics', 'knowledge-base'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`py-4 px-1 text-sm font-medium ${
                    activeTab === tab
                      ? 'border-blue-500 text-blue-600 border-b-2'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {activeTab === 'emails' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-1">
                <EmailList 
                  emails={emails} 
                  loading={loading}
                  selectedEmail={selectedEmail}
                  onSelectEmail={setSelectedEmail}
                />
              </div>
              <div className="lg:col-span-2">
                <EmailDetail 
                  email={selectedEmail} 
                  onUpdate={fetchEmails}
                />
              </div>
            </div>
          )}

          {activeTab === 'analytics' && (
            <Analytics />
          )}

          {activeTab === 'knowledge-base' && (
            <KnowledgeBase />
          )}
        </div>
      </main>
    </div>
  )
}
