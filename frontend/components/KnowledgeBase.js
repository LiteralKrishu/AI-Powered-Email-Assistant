import { useState, useEffect } from 'react'

const KnowledgeBase = () => {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [newItem, setNewItem] = useState({
    title: '',
    content: '',
    category: '',
    tags: []
  })

  useEffect(() => {
    fetchKnowledgeItems()
  }, [])

  const fetchKnowledgeItems = async () => {
    try {
      const response = await fetch('http://localhost:8000/knowledge-base/')
      const data = await response.json()
      setItems(data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching knowledge base items:', error)
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const response = await fetch('http://localhost:8000/knowledge-base/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newItem)
      })
      
      if (response.ok) {
        const createdItem = await response.json()
        setItems([createdItem, ...items])
        setNewItem({ title: '', content: '', category: '', tags: [] })
        setShowForm(false)
        alert('Knowledge base item created successfully!')
      } else:
        alert('Failed to create knowledge base item')
    } catch (error) {
      console.error('Error creating knowledge base item:', error)
      alert('Error creating knowledge base item')
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p>Loading knowledge base...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header and Add Button */}
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold">Knowledge Base</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md"
        >
          {showForm ? 'Cancel' : 'Add New Item'}
        </button>
      </div>

      {/* Add New Item Form */}
      {showForm && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium mb-4">Add New Knowledge Base Item</h3>
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Title</label>
                <input
                  type="text"
                  required
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  value={newItem.title}
                  onChange={(e) => setNewItem({ ...newItem, title: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Category</label>
                <input
                  type="text"
                  required
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  value={newItem.category}
                  onChange={(e) => setNewItem({ ...newItem, category: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Content</label>
                <textarea
                  required
                  rows={4}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  value={newItem.content}
                  onChange={(e) => setNewItem({ ...newItem, content: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Tags (comma separated)</label>
                <input
                  type="text"
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="tag1, tag2, tag3"
                  onChange={(e) => setNewItem({ 
                    ...newItem, 
                    tags: e.target.value.split(',').map(tag => tag.trim()).filter(tag => tag) 
                  })}
                />
              </div>
            </div>
            <div className="mt-4">
              <button
                type="submit"
                className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md"
              >
                Add Item
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Knowledge Base Items */}
      <div className="grid grid-cols-1 gap-4">
        {items.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-6 text-center">
            <p className="text-gray-500">No knowledge base items found</p>
          </div>
        ) : (
          items.map(item => (
            <div key={item.id} className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium">{item.title}</h3>
              <div className="flex items-center mt-2">
                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                  {item.category}
                </span>
                <span className="ml-2 text-sm text-gray-500">
                  {new Date(item.updated_at).toLocaleDateString()}
                </span>
              </div>
              {item.tags && item.tags.length > 0 && (
                <div className="mt-2">
                  {item.tags.map(tag => (
                    <span key={tag} className="inline-block px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded mr-1">
                      #{tag}
                    </span>
                  ))}
                </div>
              )}
              <p className="mt-3 text-gray-600">{item.content}</p>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default KnowledgeBase
