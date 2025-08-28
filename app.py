import React, { useState, useEffect, useRef } from 'react';

// ToastMessage Component: Displays a temporary message at the bottom of the screen
const ToastMessage = ({ message, show, type = 'info' }) => {
  if (!show) return null;

  const bgColor = {
    info: 'bg-blue-500',
    success: 'bg-green-500',
    error: 'bg-red-500',
  }[type];

  return (
    <div className={`fixed bottom-4 left-1/2 -translate-x-1/2 px-6 py-3 rounded-lg shadow-lg text-white text-lg ${bgColor} z-50 transition-opacity duration-300`}>
      {message}
    </div>
  );
};

// ConfirmationModal Component: A modal to ask the user for operation confirmation
const ConfirmationModal = ({ isOpen, message, onConfirm, onCancel }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-sm text-center">
        <p className="text-lg font-semibold mb-6">{message}</p>
        <div className="flex justify-center space-x-4">
          <button
            onClick={onConfirm}
            className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded-lg shadow-md transition duration-200"
          >
            はい
          </button>
          <button
            onClick={onCancel}
            className="bg-gray-400 hover:bg-gray-500 text-white font-bold py-2 px-4 rounded-lg shadow-md transition duration-200"
          >
            いいえ
          </button>
        </div>
      </div>
    </div>
  );
};


// Main Application Component
const App = () => {
  // State to manage the list of staff
  const [staff, setStaff] = useState(() => {
    const savedStaff = localStorage.getItem('staff');
    return savedStaff ? JSON.parse(savedStaff) : [];
  });
  // State for new staff name input
  const [newStaffName, setNewStaffName] = useState('');
  // State for new staff type input (initial value 'fixed')
  const [newStaffType, setNewStaffType] = useState('fixed');
  // State for new staff late shift availability (initial value 'true')
  const [newStaffCanWorkLateShift, setNewStaffCanWorkLateShift] = useState(true);
  // State for new staff comments
  const [newStaffComments, setNewStaffComments] = useState('');

  // State to manage the generated shift
  const [generatedShift, setGeneratedShift] = useState(() => {
    const savedShift = localStorage.getItem('generatedShift');
    return savedShift ? JSON.parse(savedShift) : {};
  });
  // List of days of the week (for Japanese display)
  const daysOfWeekJapanese = ['日', '月', '火', '水', '木', '金', '土'];
  // List of days of the week (corresponds to Date.getDay() result)
  const daysOfWeek = ['日', '月', '火', '水', '木', '金', '土'];

  // Current date for calendar display (manages month and year)
  const [currentDate, setCurrentDate] = useState(new Date());
  // ID of the flexible shift staff whose availability is currently being edited
  const [editingFlexibleStaffId, setEditingFlexibleStaffId] = useState(null);

  // State for shift editing mode
  const [editingShiftDate, setEditingShiftDate] = useState(null);
  const [tempEditingShifts, setTempEditingShifts] = useState([]);

  // Shift generation period selection (full_month, first_half, second_half)
  const [shiftPeriod, setShiftPeriod] = useState('full_month');

  // State to store previously used staff names
  const [previousStaffNames, setPreviousStaffNames] = useState(() => {
    const savedNames = localStorage.getItem('previousStaffNames');
    return savedNames ? JSON.parse(savedNames) : [];
  });

  // Staff edit modal state
  const [isStaffEditModalOpen, setIsStaffEditModalOpen] = useState(false);
  const [currentEditingStaff, setCurrentEditingStaff] = useState(null);

  // Toast message state
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('info');

  // Data clear confirmation modal state
  const [isClearConfirmModalOpen, setIsClearConfirmModalOpen] = useState(false);
  // Staff deletion confirmation modal state
  const [isDeleteStaffConfirmModalOpen, setIsDeleteStaffConfirmModalOpen] = useState(false);
  const [staffIdToDelete, setStaffIdToDelete] = useState(null);
  // Current month shift clear confirmation modal state
  const [isClearCurrentMonthShiftConfirmModalOpen, setIsClearCurrentMonthShiftConfirmModalOpen] = useState(false);


  // Reference to the hidden file input element for file loading
  const fileInputRef = useRef(null);


  // useEffect for data persistence (local storage)
  useEffect(() => {
    localStorage.setItem('staff', JSON.stringify(staff));
  }, [staff]);

  useEffect(() => {
    localStorage.setItem('generatedShift', JSON.stringify(generatedShift));
  }, [generatedShift]);

  useEffect(() => {
    localStorage.setItem('previousStaffNames', JSON.stringify(previousStaffNames));
  }, [previousStaffNames]);

  // Message indicating data has been loaded on app startup
  useEffect(() => {
    const savedStaff = localStorage.getItem('staff');
    const savedShift = localStorage.getItem('generatedShift');
    const savedNames = localStorage.getItem('previousStaffNames');

    // Display message only if actual data exists
    if (
      (savedStaff && JSON.parse(savedStaff).length > 0) ||
      (savedShift && Object.keys(JSON.parse(savedShift)).length > 0) ||
      (savedNames && JSON.parse(savedNames).length > 0)
    ) {
      setToastMessage('保存されたデータがロードされました。');
      setToastType('success');
      setShowToast(true);
      const timer = setTimeout(() => {
        setShowToast(false);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, []);


  // Helper function to format date to 'YYYY-MM-DD' string
  const formatDate = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  // List of Japanese holidays for 2025 (in YYYY-MM-DD format)
  const japaneseHolidays2025 = [
    "2025-01-01", "2025-01-13", "2025-02-11", "2025-02-24", "2025-03-20",
    "2025-04-29", "2025-05-03", "2025-05-04", "2025-05-05", "2025-05-06",
    "2025-07-21", "2025-08-11", "2025-09-15", "2025-09-23", "2025-10-13",
    "2025-11-03", "2025-11-24",
  ];

  // Function to check if a given date is a holiday
  const isHoliday = (date) => {
    if (!date) return false;
    const formatted = formatDate(date);
    return japaneseHolidays2025.includes(formatted);
  };


  // Function to add a new staff member
  const addStaff = () => {
    if (newStaffName.trim() === '') {
      setToastMessage('スタッフ名が空です。');
      setToastType('error');
      setShowToast(true);
      setTimeout(() => setShowToast(false), 3000);
      return;
    }
    const trimmedName = newStaffName.trim();
    // Create new staff object
    const newStaff = {
      id: crypto.randomUUID(),
      name: trimmedName,
      type: newStaffType,
      availability: newStaffType === 'fixed'
        ? daysOfWeek.reduce((acc, day) => ({ ...acc, [day]: false }), {})
        : newStaffType === 'flexible'
          ? []
          : true,
      canWorkLateShift: newStaffCanWorkLateShift,
      comments: newStaffComments,
    };
    setStaff([...staff, newStaff]);
    setToastMessage(`${trimmedName} を追加しました`);
    setToastType('success');
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);

    setPreviousStaffNames(prevNames => {
      const uniqueNames = new Set(prevNames);
      uniqueNames.add(trimmedName);
      const updatedNames = Array.from(uniqueNames).sort();
      return updatedNames;
    });

    setNewStaffName('');
    setNewStaffType('fixed');
    setNewStaffCanWorkLateShift(true);
    setNewStaffComments('');
  };

  // Function to open staff deletion confirmation modal
  const openDeleteStaffConfirmModal = (id) => {
    setStaffIdToDelete(id);
    setIsDeleteStaffConfirmModalOpen(true);
  };

  // Function to confirm staff deletion
  const confirmDeleteStaff = () => {
    const staffToDelete = staff.find(s => s.id === staffIdToDelete);
    if (staffToDelete) {
      setStaff(staff.filter(s => s.id !== staffIdToDelete));
      setToastMessage(`${staffToDelete.name} を削除しました。`);
      setToastType('info');
      setShowToast(true);
      setTimeout(() => setShowToast(false), 3000);

      if (editingFlexibleStaffId === staffIdToDelete) {
        setEditingFlexibleStaffId(null);
      }
    }
    setIsDeleteStaffConfirmModalOpen(false);
    setStaffIdToDelete(null);
  };

  // Function to cancel staff deletion
  const cancelDeleteStaff = () => {
    setIsDeleteStaffConfirmModalOpen(false);
    setStaffIdToDelete(null);
  };

  // Function to update fixed shift staff's availability
  const updateFixedStaffAvailability = (staffId, day, isAvailable) => {
    if (day === '月') {
      setToastMessage('月曜日は定休日なので、出勤可能状況は変更できません。');
      setToastType('error');
      setShowToast(true);
      setTimeout(() => setShowToast(false), 3000);
      return;
    }

    setStaff(
      staff.map((s) =>
        s.id === staffId && s.type === 'fixed'
          ? { ...s, availability: { ...s.availability, [day]: isAvailable } }
          : s
      )
    );
  };

  // Function to toggle flexible shift staff's availability (date)
  const toggleFlexibleStaffAvailability = (staffId, date) => {
    setStaff(
      staff.map((s) => {
        if (s.id === staffId && s.type === 'flexible') {
          const dateString = formatDate(date);
          const newAvailability = s.availability.includes(dateString)
            ? s.availability.filter((d) => d !== dateString)
            : [...s.availability, dateString];
          return { ...s, availability: newAvailability };
        }
        return s;
      })
    );
  };

  // Function to automatically generate shifts
  const generateShift = () => {
    if (staff.length === 0) {
      setToastMessage('スタッフが登録されていません。');
      setToastType('error');
      setShowToast(true);
      setTimeout(() => setShowToast(false), 3000);
      return;
    }

    const newShift = {};
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    const numDaysInMonth = new Date(year, month + 1, 0).getDate();
    let startDay = 1;
    let endDay = numDaysInMonth;

    if (shiftPeriod === 'first_half') {
      endDay = Math.floor(numDaysInMonth / 2);
    } else if (shiftPeriod === 'second_half') {
      startDay = Math.floor(numDaysInMonth / 2) + 1;
    }

    for (let i = startDay; i <= endDay; i++) {
      const currentDayDate = new Date(year, month, i);
      const dayOfWeekIndex = currentDayDate.getDay();
      const dayOfWeekName = daysOfWeek[dayOfWeekIndex];
      const formattedDate = formatDate(currentDayDate);

      // Mondays are regular holidays
      if (dayOfWeekName === '月') {
        newShift[formattedDate] = [{ staff: '定休日', startTime: '', endTime: '', comments: '' }];
        continue;
      }

      let requiredShifts = [];
      if (dayOfWeekName === '土') {
        requiredShifts = [{ startTime: '19:00', endTime: '23:00' }, { startTime: '17:00', endTime: '22:00' }];
      } else if (['火', '水', '木'].includes(dayOfWeekName)) {
        requiredShifts = [{ startTime: '18:00', endTime: '22:00' }];
      } else if (['金', '日'].includes(dayOfWeekName)) {
        requiredShifts = [{ startTime: '17:00', endTime: '22:00' }];
      }

      if (isHoliday(currentDayDate)) {
        requiredShifts = requiredShifts.map(shift => ({
          ...shift,
          startTime: '17:00'
        }));
      }

      const assignedStaffForDay = [];
      const assignedStaffIds = new Set();

      for (const shift of requiredShifts) {
        let staffToAssign = null;

        const getEligibleStaff = (staffType) => {
          const eligible = staff.filter(s => {
            if (s.type !== staffType) return false;

            const isAvailableByType =
              (s.type === 'flexible' && s.availability.includes(formattedDate)) ||
              (s.type === 'fixed' && s.availability[dayOfWeekName]) ||
              (s.type === 'anytime' && s.availability === true);

            const canWorkLateShift = s.comments?.includes('遅番不可') ? shift.startTime !== '19:00' : true;
            const canWorkThisShiftTime = (shift.startTime === '19:00' && s.canWorkLateShift) || shift.startTime !== '19:00';
            const isNotAlreadyAssigned = !assignedStaffIds.has(s.id);

            return isAvailableByType && canWorkLateShift && canWorkThisShiftTime && isNotAlreadyAssigned;
          });

          for (let k = eligible.length - 1; k > 0; k--) {
            const j = Math.floor(Math.random() * (k + 1));
            [eligible[k], eligible[j]] = [eligible[j], eligible[k]];
          }
          return eligible;
        };

        const availableFlexibleStaff = getEligibleStaff('flexible');
        if (availableFlexibleStaff.length > 0) {
          staffToAssign = availableFlexibleStaff[0];
        }

        if (!staffToAssign) {
          const availableFixedStaff = getEligibleStaff('fixed');
          if (availableFixedStaff.length > 0) {
            staffToAssign = availableFixedStaff[0];
          }
        }

        if (!staffToAssign) {
          const availableAnytimeStaff = getEligibleStaff('anytime');
          if (availableAnytimeStaff.length > 0) {
            staffToAssign = availableAnytimeStaff[0];
          }
        }

        if (staffToAssign) {
          assignedStaffForDay.push({ staff: staffToAssign.name, startTime: shift.startTime, endTime: shift.endTime, comments: '' });
          assignedStaffIds.add(staffToAssign.id);
        } else {
          assignedStaffForDay.push({ staff: '未割り当て', startTime: shift.startTime, endTime: shift.endTime, comments: '' });
        }
      }
      newShift[formattedDate] = assignedStaffForDay;
    }
    setGeneratedShift(newShift);
    setToastMessage('シフトを自動生成しました。');
    setToastType('success');
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  // Function to move to the previous month in the calendar
  const goToPreviousMonth = () => {
    setCurrentDate(prevDate => {
      const newDate = new Date(prevDate);
      newDate.setMonth(newDate.getMonth() - 1);
      return newDate;
    });
    setEditingFlexibleStaffId(null);
    setEditingShiftDate(null);
  };

  // Function to move to the next month in the calendar
  const goToNextMonth = () => {
    setCurrentDate(prevDate => {
      const newDate = new Date(prevDate);
      newDate.setMonth(newDate.getMonth() + 1);
      return newDate;
    });
    setEditingFlexibleStaffId(null);
    setEditingShiftDate(null);
  };

  // Function to generate calendar days for the specified month
  const generateCalendarDays = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();

    const firstDayOfMonth = new Date(year, month, 1);
    const lastDayOfMonth = new Date(year, month + 1, 0);
    const numDaysInMonth = lastDayOfMonth.getDate();

    const calendarDays = [];

    for (let i = 0; i < firstDayOfMonth.getDay(); i++) {
      calendarDays.push(null);
    }

    for (let i = 1; i <= numDaysInMonth; i++) {
      calendarDays.push(new Date(year, month, i));
    }

    const totalCells = calendarDays.length;
    const remainingCells = 42 - totalCells;
    for (let i = 0; i < remainingCells; i++) {
      calendarDays.push(null);
    }

    return calendarDays;
  };

  const calendarDays = generateCalendarDays(currentDate);

  // Get information of the flexible shift staff currently being edited
  const currentFlexibleStaff = staff.find(s => s.id === editingFlexibleStaffId);

  // Function to enter shift editing mode
  const handleEditShift = (date) => {
    setEditingShiftDate(date);
    setTempEditingShifts([...(generatedShift[date] || [])]);
  };

  // Function to temporarily reflect staff or time changes in editing mode
  const handleShiftDetailChange = (shiftIndex, field, value) => {
    const updatedShifts = [...tempEditingShifts];
    updatedShifts[shiftIndex] = { ...updatedShifts[shiftIndex], [field]: value };
    setTempEditingShifts(updatedShifts);
  };

  // Function to save shift edits
  const handleSaveShift = () => {
    setGeneratedShift(prev => ({
      ...prev,
      [editingShiftDate]: tempEditingShifts,
    }));
    setEditingShiftDate(null);
    setTempEditingShifts([]);
    setToastMessage('シフトを保存しました。');
    setToastType('success');
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  // Function to cancel shift edits
  const handleCancelEdit = () => {
    setEditingShiftDate(null);
    setTempEditingShifts([]);
    setToastMessage('シフト編集をキャンセルしました。');
    setToastType('info');
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  // Function to export generated shifts as CSV
  const exportShiftToCsv = () => {
    if (Object.keys(generatedShift).length === 0) {
      setToastMessage('生成されたシフトがありません。');
      setToastType('error');
      setShowToast(true);
      setTimeout(() => setShowToast(false), 3000);
      return;
    }

    const csvRows = [];
    const staffNames = staff.map(s => s.name);

    csvRows.push(['\uFEFF日付', ...staffNames].join(','));

    const filteredCalendarDays = calendarDays.filter(day => {
      if (!day || day.getMonth() !== currentDate.getMonth()) return false;
      const dayOfMonth = day.getDate();
      const numDays = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();
      const halfPoint = Math.floor(numDays / 2);
      if (shiftPeriod === 'first_half' && dayOfMonth > halfPoint) return false;
      if (shiftPeriod === 'second_half' && dayOfMonth <= halfPoint) return false;
      return true;
    });

    filteredCalendarDays.forEach(day => {
      const formattedDate = formatDate(day);
      const shiftsForDay = generatedShift[formattedDate] || [];
      const row = [
        `${day.getMonth() + 1}月${day.getDate()}日 (${daysOfWeekJapanese[day.getDay()]})`
      ];

      if (day.getDay() === 1) {
        row.push(...Array(staffNames.length).fill('定休日'));
      } else {
        staffNames.forEach(sName => {
          const staffShifts = shiftsForDay.filter(shift => shift.staff === sName);
          const displayTimes = staffShifts.map(shift => {
            return `${shift.startTime || ''}-${shift.endTime || ''}`;
          }).join(';');
          row.push(displayTimes || '');
        });
      }
      csvRows.push(row.join('\n'));
    });

    const csvString = csvRows.join('\n');
    const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `shift_schedule_${formatDate(currentDate)}_${shiftPeriod}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    setToastMessage('シフトデータをCSVとしてエクスポートしました。');
    setToastType('success');
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  // Function to open staff edit modal
  const openStaffEditModal = (staffId) => {
    const staffToEdit = staff.find(s => s.id === staffId);
    if (staffToEdit) {
      setCurrentEditingStaff({ ...staffToEdit });
      setCurrentEditingStaff(prev => ({
        ...prev,
        canWorkLateShift: prev.canWorkLateShift !== undefined ? prev.canWorkLateShift : true,
        comments: prev.comments !== undefined ? prev.comments : '',
      }));
      setIsStaffEditModalOpen(true);
    }
  };

  // Function to close staff edit modal
  const closeStaffEditModal = () => {
    setIsStaffEditModalOpen(false);
    setCurrentEditingStaff(null);
  };

  // Handler for input changes in staff edit modal
  const handleCurrentEditingStaffChange = (e) => {
    const { name, value, type, checked } = e.target;
    if (name === 'availability') {
      setCurrentEditingStaff(prev => ({
        ...prev,
        availability: {
          ...prev.availability,
          [value]: checked
        }
      }));
    } else if (name === 'canWorkLateShift') {
      setCurrentEditingStaff(prev => ({
        ...prev,
        canWorkLateShift: checked
      }));
    } else {
      setCurrentEditingStaff(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  // Handler to save staff edits in modal
  const saveStaffEdit = () => {
    if (currentEditingStaff) {
      setStaff(prevStaff => prevStaff.map(s =>
        s.id === currentEditingStaff.id ? currentEditingStaff : s
      ));
      setPreviousStaffNames(prevNames => {
        const uniqueNames = new Set(prevNames);
        uniqueNames.add(currentEditingStaff.name);
        return Array.from(uniqueNames).sort();
      });
      setToastMessage(`${currentEditingStaff.name} の情報を保存しました。`);
      setToastType('success');
      setShowToast(true);
      setTimeout(() => setShowToast(false), 3000);
      closeStaffEditModal();
    }
  };

  // Function to clear all data from local storage
  const handleClearAllData = () => {
    setIsClearConfirmModalOpen(true);
  };

  const confirmClearData = () => {
    localStorage.removeItem('staff');
    localStorage.removeItem('generatedShift');
    localStorage.removeItem('previousStaffNames');
    setStaff([]);
    setGeneratedShift({});
    setPreviousStaffNames([]);
    setNewStaffName('');
    setNewStaffType('fixed');
    setNewStaffComments('');
    setEditingFlexibleStaffId(null);
    setEditingShiftDate(null);
    setTempEditingShifts([]);
    setShiftPeriod('full_month');
    setToastMessage('全てのデータが削除されました。');
    setToastType('info');
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
    setIsClearConfirmModalOpen(false);
  };

  const cancelClearData = () => {
    setIsClearConfirmModalOpen(false);
  };

  // Function to save app data as a file
  const handleSaveToFile = () => {
    if (staff.length === 0 && Object.keys(generatedShift).length === 0) {
      setToastMessage('保存するデータがありません。');
      setToastType('error');
      setShowToast(true);
      setTimeout(() => setShowToast(false), 3000);
      return;
    }

    const appData = {
      staff: staff,
      generatedShift: generatedShift,
      previousStaffNames: previousStaffNames,
    };
    const jsonString = JSON.stringify(appData, null, 2);

    const now = new Date();
    const filename = `shift_data_${formatDate(now)}_${now.getHours()}${String(now.getMinutes()).padStart(2, '0')}${String(now.getSeconds()).padStart(2, '0')}.json`;

    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    setToastMessage('アプリデータをファイルに保存しました。');
    setToastType('success');
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  // Function to load app data from a file
  const handleLoadFromFile = (event) => {
    const file = event.target.files[0];
    if (!file) {
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const loadedData = JSON.parse(e.target.result);
        if (loadedData.staff && loadedData.generatedShift && loadedData.previousStaffNames) {
          const updatedStaff = loadedData.staff.map(s => ({
            ...s,
            canWorkLateShift: s.canWorkLateShift !== undefined ? s.canWorkLateShift : true,
            comments: s.comments !== undefined ? s.comments : '',
          }));

          setStaff(updatedStaff);
          setGeneratedShift(loadedData.generatedShift);
          setPreviousStaffNames(loadedData.previousStaffNames);
          setToastMessage('アプリデータをファイルから読み込みました。');
          setToastType('success');
          setShowToast(true);
          setTimeout(() => setShowToast(false), 3000);
        } else {
          setToastMessage('無効なファイル形式です。');
          setToastType('error');
          setShowToast(true);
          setTimeout(() => setShowToast(false), 3000);
        }
      } catch (error) {
        setToastMessage('ファイルの読み込み中にエラーが発生しました。');
        setToastType('error');
        setShowToast(true);
        setTimeout(() => setShowToast(false), 3000);
        console.error("Error loading file:", error);
      }
    };
    reader.readAsText(file);
    event.target.value = null;
  };

  // Trigger the hidden file input element when "Load from File" button is clicked
  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  // Function to clear current month's shifts (opens confirmation modal)
  const handleClearCurrentMonthShift = () => {
    const currentMonthYear = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}`;
    const hasShiftForCurrentMonth = Object.keys(generatedShift).some(dateKey =>
      dateKey.startsWith(currentMonthYear)
    );

    if (!hasShiftForCurrentMonth) {
      setToastMessage('当月のシフトデータがありません。');
      setToastType('info');
      setShowToast(true);
      setTimeout(() => setShowToast(false), 3000);
      return;
    }
    setIsClearCurrentMonthShiftConfirmModalOpen(true);
  };

  // Function to confirm clearing current month's shifts
  const confirmClearCurrentMonthShift = () => {
    const currentMonthYear = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}`;
    const updatedShift = {};
    for (const dateKey in generatedShift) {
      if (!dateKey.startsWith(currentMonthYear)) {
        updatedShift[dateKey] = generatedShift[dateKey];
      }
    }
    setGeneratedShift(updatedShift);
    setToastMessage('当月のシフトをクリアしました。');
    setToastType('info');
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
    setIsClearCurrentMonthShiftConfirmModalOpen(false);
  };

  // Function to cancel clearing current month's shifts
  const cancelClearCurrentMonthShift = () => {
    setIsClearCurrentMonthShiftConfirmModalOpen(false);
  };

  // Determine if there is shift data for the current month to enable/disable the clear button
  const hasCurrentMonthShift = Object.keys(generatedShift).some(dateKey =>
    dateKey.startsWith(`${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}`)
  );


  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4 font-inter text-gray-800">
      <div className="max-w-4xl mx-auto bg-white rounded-xl shadow-2xl p-6 sm:p-8 space-y-8">
        <h1 className="text-4xl font-extrabold text-center text-indigo-700 mb-8 tracking-tight">
          シフト管理アプリ
        </h1>

        {/* スタッフ追加セクション */}
        <section className="bg-blue-50 p-4 sm:p-6 rounded-lg shadow-inner">
          <h2 className="text-xl sm:text-2xl font-bold text-indigo-600 mb-4">スタッフの追加</h2>
          <div className="flex flex-col gap-4 mb-4 items-stretch">
            <input
              type="text"
              list="previous-names"
              className="w-full p-3 border border-blue-200 rounded-lg focus:ring-2 focus:ring-blue-400 focus:border-transparent outline-none transition duration-200"
              placeholder="新しいスタッフの名前を入力"
              value={newStaffName}
              onChange={(e) => setNewStaffName(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  addStaff();
                }
              }}
            />
            {/* Datalist for previous name suggestions */}
            <datalist id="previous-names">
              {previousStaffNames.map(name => (
                <option key={name} value={name} />
              ))}
            </datalist>

            <div className="flex flex-wrap justify-center sm:justify-between space-x-2 space-y-2 sm:space-y-0 sm:space-x-4">
              <label className="inline-flex items-center">
                <input
                  type="radio"
                  name="newStaffType"
                  value="fixed"
                  checked={newStaffType === 'fixed'}
                  onChange={(e) => setNewStaffType(e.target.value)}
                  className="form-radio h-4 w-4 text-indigo-600"
                />
                <span className="ml-2 text-gray-700">固定シフト</span>
              </label>
              <label className="inline-flex items-center">
                <input
                  type="radio"
                  name="newStaffType"
                  value="flexible"
                  checked={newStaffType === 'flexible'}
                  onChange={(e) => setNewStaffType(e.target.value)}
                  className="form-radio h-4 w-4 text-indigo-600"
                />
                <span className="ml-2 text-gray-700">変動シフト</span>
              </label>
              <label className="inline-flex items-center">
                <input
                  type="radio"
                  name="newStaffType"
                  value="anytime"
                  checked={newStaffType === 'anytime'}
                  onChange={(e) => setNewStaffType(e.target.value)}
                  className="form-radio h-4 w-4 text-indigo-600"
                />
                <span className="ml-2 text-gray-700">いつでも可</span>
              </label>
            </div>
            <button
              onClick={addStaff}
              className="w-full bg-indigo-500 hover:bg-indigo-600 text-white font-semibold py-3 px-6 rounded-lg shadow-md transform hover:scale-105 transition duration-200 ease-in-out"
            >
              追加
            </button>
          </div>
        </section>

        {/* スタッフと出勤可能状況リストセクション */}
        <section className="bg-purple-50 p-4 sm:p-6 rounded-lg shadow-inner">
          <h2 className="text-xl sm:text-2xl font-bold text-purple-600 mb-4">スタッフの出勤可能状況</h2>
          {staff.length === 0 ? (
            <p className="text-gray-500 text-center py-4">スタッフを追加してください。</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full bg-white rounded-lg shadow-md">
                <thead className="bg-purple-100">
                  <tr>
                    <th className="py-2 px-2 text-left text-sm font-medium text-purple-700 uppercase tracking-wider rounded-tl-lg">
                      名前
                    </th>
                    <th className="py-2 px-2 text-left text-sm font-medium text-purple-700 uppercase tracking-wider hidden sm:table-cell">
                      タイプ
                    </th>
                    <th className="py-2 px-2 text-center text-sm font-medium text-purple-700 uppercase tracking-wider">
                      操作
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {staff.map((s) => (
                    <tr key={s.id} className="border-t border-purple-200 hover:bg-purple-50 transition duration-150">
                      <td className="py-3 px-2 whitespace-nowrap text-base font-medium text-gray-900">
                        {s.name}
                      </td>
                      <td className="py-3 px-2 whitespace-nowrap text-base text-gray-700 hidden sm:table-cell">
                        {s.type === 'fixed' ? '固定' : s.type === 'flexible' ? '変動' : 'いつでも可'}
                      </td>
                      <td className="py-3 px-2 whitespace-nowrap flex space-x-2 justify-center items-center">
                        {s.type === 'fixed' && (
                          <button
                            onClick={() => openStaffEditModal(s.id)}
                            className="bg-yellow-500 hover:bg-yellow-600 text-white text-sm font-semibold py-1 px-3 rounded-lg shadow-md transform hover:scale-105 transition duration-200 ease-in-out"
                          >
                            曜日設定
                          </button>
                        )}
                        {s.type === 'flexible' && (
                          <button
                            onClick={() => {
                              try {
                                setEditingFlexibleStaffId(s.id);
                              } catch (error) {
                                console.error("日付設定モードへの移行中にエラーが発生しました:", error);
                              }
                            }}
                            className="bg-blue-400 hover:bg-blue-500 text-white text-sm font-semibold py-1 px-3 rounded-lg shadow-md transform hover:scale-105 transition duration-200 ease-in-out"
                          >
                            日付設定
                          </button>
                        )}
                        {s.type === 'anytime' && (
                          <button
                            onClick={() => openStaffEditModal(s.id)}
                            className="bg-yellow-500 hover:bg-yellow-600 text-white text-sm font-semibold py-1 px-3 rounded-lg shadow-md transform hover:scale-105 transition duration-200 ease-in-out"
                          >
                            編集
                          </button>
                        )}
                        <button
                          onClick={() => openDeleteStaffConfirmModal(s.id)}
                          className="bg-red-500 hover:bg-red-600 text-white text-sm font-semibold py-1 px-3 rounded-lg shadow-md transform hover:scale-105 transition duration-200 ease-in-out"
                        >
                          削除
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {/* スタッフ編集モーダル */}
        {isStaffEditModalOpen && currentEditingStaff && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
              <h3 className="text-2xl font-bold text-indigo-700 mb-6 text-center">スタッフ情報を編集</h3>
              <div className="space-y-4">
                <div>
                  <label htmlFor="editStaffName" className="block text-gray-700 text-sm font-bold mb-2">
                    スタッフ名:
                  </label>
                  <input
                    type="text"
                    id="editStaffName"
                    name="name"
                    value={currentEditingStaff.name}
                    onChange={handleCurrentEditingStaffChange}
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  />
                </div>
                <div>
                  <span className="block text-gray-700 text-sm font-bold mb-2">タイプ:</span>
                  <div className="flex flex-wrap gap-2">
                    <label className="inline-flex items-center">
                      <input
                        type="radio"
                        name="type"
                        value="fixed"
                        checked={currentEditingStaff.type === 'fixed'}
                        onChange={handleCurrentEditingStaffChange}
                        className="form-radio h-4 w-4 text-indigo-600"
                      />
                      <span className="ml-2 text-gray-700">固定シフト</span>
                    </label>
                    <label className="inline-flex items-center">
                      <input
                        type="radio"
                        name="type"
                        value="flexible"
                        checked={currentEditingStaff.type === 'flexible'}
                        onChange={handleCurrentEditingStaffChange}
                        className="form-radio h-4 w-4 text-indigo-600"
                      />
                      <span className="ml-2 text-gray-700">変動シフト</span>
                    </label>
                    <label className="inline-flex items-center">
                      <input
                        type="radio"
                        name="type"
                        value="anytime"
                        checked={currentEditingStaff.type === 'anytime'}
                        onChange={handleCurrentEditingStaffChange}
                        className="form-radio h-4 w-4 text-indigo-600"
                      />
                      <span className="ml-2 text-gray-700">いつでも可</span>
                    </label>
                  </div>
                </div>
                <div>
                  <label className="inline-flex items-center">
                    <input
                      type="checkbox"
                      name="canWorkLateShift"
                      checked={currentEditingStaff.canWorkLateShift}
                      onChange={handleCurrentEditingStaffChange}
                      className="form-checkbox h-5 w-5 text-indigo-600 rounded"
                    />
                    <span className="ml-2 text-gray-700">遅番（19:00入り）可能</span>
                  </label>
                </div>
                <div>
                    <label htmlFor="editStaffComments" className="block text-gray-700 text-sm font-bold mb-2">
                      特記事項（金曜日のみ18:00から、遅番不可など）:
                    </label>
                    <input
                      type="text"
                      id="editStaffComments"
                      name="comments"
                      value={currentEditingStaff.comments || ''}
                      onChange={handleCurrentEditingStaffChange}
                      className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                      placeholder="例: 18:00から, 遅番不可"
                    />
                </div>

                {currentEditingStaff.type === 'fixed' && (
                  <div>
                    <span className="block text-gray-700 text-sm font-bold mb-2">出勤可能曜日:</span>
                    <div className="grid grid-cols-4 gap-2">
                      {daysOfWeek.map((day, index) => (
                        <label key={day} className="inline-flex items-center">
                          <input
                            type="checkbox"
                            name="availability"
                            value={day}
                            checked={currentEditingStaff.availability[day] || false}
                            onChange={handleCurrentEditingStaffChange}
                            disabled={day === '月'}
                            className="form-checkbox h-5 w-5 text-purple-600 rounded"
                          />
                          <span className="ml-2 text-gray-700">{daysOfWeekJapanese[index]}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              <div className="flex justify-end space-x-4 mt-8">
                <button
                  onClick={saveStaffEdit}
                  className="bg-indigo-500 hover:bg-indigo-600 text-white font-bold py-2 px-4 rounded-lg shadow-md transition duration-200"
                >
                  保存
                </button>
                <button
                  onClick={closeStaffEditModal}
                  className="bg-gray-400 hover:bg-gray-500 text-white font-bold py-2 px-4 rounded-lg shadow-md transition duration-200"
                >
                  キャンセル
                </button>
              </div>
            </div>
          </div>
        )}

        {/* シフト生成ボタン */}
        <section className="text-center bg-green-50 p-4 sm:p-6 rounded-lg shadow-inner">
          <h2 className="text-xl sm:text-2xl font-bold text-green-600 mb-4">シフト生成期間</h2>
          <div className="flex justify-center space-x-2 sm:space-x-4 mb-6">
            <label className="inline-flex items-center">
              <input
                type="radio"
                name="shiftPeriod"
                value="full_month"
                checked={shiftPeriod === 'full_month'}
                onChange={(e) => setShiftPeriod(e.target.value)}
                className="form-radio h-4 w-4 text-green-600"
              />
              <span className="ml-2 text-gray-700 text-sm sm:text-base">全月</span>
            </label>
            <label className="inline-flex items-center">
              <input
                type="radio"
                name="shiftPeriod"
                value="first_half"
                checked={shiftPeriod === 'first_half'}
                onChange={(e) => setShiftPeriod(e.target.value)}
                className="form-radio h-4 w-4 text-green-600"
              />
              <span className="ml-2 text-gray-700 text-sm sm:text-base">前半</span>
            </label>
            <label className="inline-flex items-center">
              <input
                type="radio"
                name="shiftPeriod"
                value="second_half"
                checked={shiftPeriod === 'second_half'}
                onChange={(e) => setShiftPeriod(e.target.value)}
                className="form-radio h-4 w-4 text-green-600"
              />
              <span className="ml-2 text-gray-700 text-sm sm:text-base">後半</span>
            </label>
          </div>
          <button
            onClick={generateShift}
            className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-4 px-10 rounded-full shadow-lg transform hover:scale-105 transition duration-300 ease-in-out text-xl"
          >
            シフトを自動生成
          </button>
        </section>

        {/* 生成されたシフト表示セクション */}
        <section className="bg-teal-50 p-4 sm:p-6 rounded-lg shadow-inner">
          <h2 className="text-xl sm:text-2xl font-bold text-teal-600 mb-4">生成されたシフト</h2>
          {Object.keys(generatedShift).length === 0 ? (
            <p className="text-gray-500 text-center py-4">
              シフトを生成するとここに表示されます。
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full bg-white rounded-lg shadow-md">
                <thead className="bg-teal-100">
                  <tr>
                    <th className="py-2 px-2 text-left text-sm font-medium text-teal-700 uppercase tracking-wider rounded-tl-lg">
                      日付
                    </th>
                    {staff.map((s) => (
                      <th key={s.id} className="py-2 px-2 text-center text-sm font-medium text-teal-700 uppercase tracking-wider">
                        {s.name}
                      </th>
                    ))}
                    <th className="py-2 px-2 text-center text-sm font-medium text-teal-700 uppercase tracking-wider">
                      操作
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {calendarDays.filter(day => {
                    if (!day || day.getMonth() !== currentDate.getMonth()) return false;
                    const dayOfMonth = day.getDate();
                    const numDays = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();
                    const halfPoint = Math.floor(numDays / 2);
                    if (shiftPeriod === 'first_half' && dayOfMonth > halfPoint) return false;
                    if (shiftPeriod === 'second_half' && dayOfMonth <= halfPoint) return false;
                    return true;
                  }).map((day) => {
                    const formattedDate = formatDate(day);
                    const shiftsForDay = generatedShift[formattedDate] || [];
                    const isMonday = day.getDay() === 1;

                    return (
                      <tr key={formattedDate} className="border-t border-teal-200 hover:bg-teal-50 transition duration-150">
                        <td className="py-2 px-2 whitespace-nowrap text-base font-medium text-gray-900">
                          {day.getMonth() + 1}月{day.getDate()}日 ({daysOfWeekJapanese[day.getDay()]})
                        </td>
                        {staff.map((s) => {
                          if (isMonday) {
                            return (
                              <td key={s.id} className="py-2 px-2 text-center text-gray-500">
                                定休日
                              </td>
                            );
                          }
                          if (editingShiftDate === formattedDate) {
                            const staffShifts = tempEditingShifts.filter(shift => shift.staff === s.name);
                            return (
                              <td key={s.id} className="py-2 px-2 text-center">
                                {staffShifts.length > 0 ? (
                                  staffShifts.map((shift, idx) => (
                                    <div key={idx} className="mb-1 flex flex-col items-center">
                                      <select
                                        value={shift.staff}
                                        onChange={(e) => handleShiftDetailChange(tempEditingShifts.indexOf(shift), 'staff', e.target.value)}
                                        className="p-1 border rounded-md text-sm w-full mb-1"
                                      >
                                        <option value="未割り当て">未割り当て</option>
                                        {staff.map(allStaff => (
                                          <option key={allStaff.id} value={allStaff.name}>
                                            {allStaff.name}
                                          </option>
                                        ))}
                                      </select>
                                      <div className="flex space-x-1 w-full">
                                        <input
                                          type="time"
                                          value={shift.startTime || ''}
                                          onChange={(e) => handleShiftDetailChange(tempEditingShifts.indexOf(shift), 'startTime', e.target.value)}
                                          className="p-1 border rounded-md text-sm w-1/2"
                                        />
                                        <span className="flex items-center">-</span>
                                        <input
                                          type="time"
                                          value={shift.endTime || ''}
                                          onChange={(e) => handleShiftDetailChange(tempEditingShifts.indexOf(shift), 'endTime', e.target.value)}
                                          className="p-1 border rounded-md text-sm w-1/2"
                                        />
                                      </div>
                                    </div>
                                  ))
                                ) : (
                                  <select
                                    value="未割り当て"
                                    onChange={(e) => {}}
                                    className="p-1 border rounded-md text-sm w-full"
                                    disabled
                                  >
                                    <option value="未割り当て">—</option>
                                  </select>
                                )}
                              </td>
                            );
                          }

                          const staffShifts = shiftsForDay.filter(shift => shift.staff === s.name);
                          const displayTimes = staffShifts.map(shift => {
                            return `(${shift.startTime} - ${shift.endTime})`;
                          }).join(', ');
                          return (
                            <td key={s.id} className="py-2 px-2 text-center text-base text-gray-700">
                              {displayTimes || '—'}
                            </td>
                          );
                        })}
                        <td className="py-2 px-2 whitespace-nowrap text-center">
                          {editingShiftDate === formattedDate ? (
                            <div className="flex flex-col space-y-2">
                              <button
                                onClick={handleSaveShift}
                                className="bg-green-500 hover:bg-green-600 text-white text-sm font-semibold py-1 px-3 rounded-lg shadow-md"
                              >
                                保存
                              </button>
                              <button
                                onClick={handleCancelEdit}
                                className="bg-gray-400 hover:bg-gray-500 text-white text-sm font-semibold py-1 px-3 rounded-lg shadow-md"
                              >
                                キャンセル
                              </button>
                            </div>
                          ) : (
                            <button
                              onClick={() => handleEditShift(formattedDate)}
                              className="bg-blue-500 hover:bg-blue-600 text-white text-sm font-semibold py-1 px-3 rounded-lg shadow-md"
                            >
                              編集
                            </button>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
              {Object.keys(generatedShift).length > 0 && (
                <div className="text-center mt-6">
                  <button
                    onClick={exportShiftToCsv}
                    className="w-full sm:w-auto bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-8 rounded-full shadow-lg transform hover:scale-105 transition duration-300 ease-in-out text-lg"
                  >
                    スプレッドシートに出力
                  </button>
                </div>
              )}
            </div>
          )}
        </section>

        {/* データ管理ボタンセクション (常に表示) */}
        <section className="text-center bg-gray-50 p-4 sm:p-6 rounded-lg shadow-inner">
          <h2 className="text-xl sm:text-2xl font-bold text-gray-700 mb-4">データ管理</h2>
          <div className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-4">
            {staff.length > 0 || Object.keys(generatedShift).length > 0 ? (
              <button
                onClick={handleSaveToFile}
                className="w-full sm:w-auto bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-8 rounded-full shadow-lg transform hover:scale-105 transition duration-300 ease-in-out text-lg"
              >
                データをファイルに保存
              </button>
            ) : (
              <button
                disabled
                className="w-full sm:w-auto bg-indigo-300 text-white font-bold py-3 px-8 rounded-full shadow-lg cursor-not-allowed text-lg"
              >
                データをファイルに保存
              </button>
            )}
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleLoadFromFile}
              style={{ display: 'none' }}
              accept=".json"
            />
            <button
              onClick={triggerFileInput}
              className="w-full sm:w-auto bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-8 rounded-full shadow-lg transform hover:scale-105 transition duration-300 ease-in-out text-lg"
            >
              ファイルから読み込む
            </button>
            {hasCurrentMonthShift ? (
              <button
                onClick={handleClearCurrentMonthShift}
                className="w-full sm:w-auto bg-orange-600 hover:bg-orange-700 text-white font-bold py-3 px-8 rounded-full shadow-lg transform hover:scale-105 transition duration-300 ease-in-out text-lg"
              >
                当月のシフトをクリア
              </button>
            ) : (
              <button
                disabled
                className="w-full sm:w-auto bg-orange-300 text-white font-bold py-3 px-8 rounded-full shadow-lg cursor-not-allowed text-lg"
              >
                当月のシフトをクリア
              </button>
            )}
            <button
              onClick={handleClearAllData}
              className="w-full sm:w-auto bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-8 rounded-full shadow-lg transform hover:scale-105 transition duration-300 ease-in-out text-lg"
            >
                全てのデータをクリア
            </button>
          </div>
        </section>


        {/* カレンダー表示セクション */}
        <section className="bg-orange-50 p-4 sm:p-6 rounded-lg shadow-inner">
          <h2 className="text-xl sm:text-2xl font-bold text-orange-600 mb-4 text-center">
            シフトカレンダー
            {editingFlexibleStaffId && (
              <span className="block text-blue-700 text-lg sm:text-xl">
                ({currentFlexibleStaff?.name}さんの出勤日設定中)
              </span>
            )}
          </h2>
          <div className="flex justify-between items-center mb-4">
            <button
              onClick={goToPreviousMonth}
              className="bg-orange-400 hover:bg-orange-500 text-white font-bold py-2 px-4 rounded-lg shadow-md transform hover:scale-105 transition duration-200 ease-in-out"
            >
              &lt; 前の月
            </button>
            <h3 className="text-xl font-semibold text-orange-700">
              {currentDate.getFullYear()}年 {currentDate.getMonth() + 1}月
            </h3>
            <button
              onClick={goToNextMonth}
              className="bg-orange-400 hover:bg-orange-500 text-white font-bold py-2 px-4 rounded-lg shadow-md transform hover:scale-105 transition duration-200 ease-in-out"
            >
              次の月 &gt;
            </button>
          </div>
          <div className="grid grid-cols-7 gap-1 text-center">
            {daysOfWeekJapanese.map((day) => (
              <div key={day} className="font-bold text-orange-700 py-2 bg-orange-100 rounded-md">
                {day}
              </div>
            ))}
            {calendarDays.map((day, index) => {
              const isCurrentMonth = day && day.getMonth() === currentDate.getMonth();
              const isFlexibleStaffEditing = editingFlexibleStaffId !== null;
              const isMonday = day && day.getDay() === 1;
              const isCurrentDayHoliday = isHoliday(day);

              const isAvailableForEditingStaff = currentFlexibleStaff && day && currentFlexibleStaff.availability.includes(formatDate(day));

              return (
                <div
                  key={index}
                  className={`p-2 rounded-md ${
                    day
                      ? 'bg-white shadow-sm'
                      : 'bg-gray-100'
                  } ${
                    isCurrentMonth
                      ? 'text-gray-800'
                      : 'text-gray-400'
                  } flex flex-col items-center justify-center min-h-[80px] sm:min-h-[100px]
                  ${isFlexibleStaffEditing && isCurrentMonth && !isMonday ? 'cursor-pointer hover:bg-blue-100' : ''}
                  ${isFlexibleStaffEditing && isAvailableForEditingStaff && !isMonday ? 'bg-blue-200 border-2 border-blue-500' : ''}
                  ${isMonday ? 'bg-gray-300 text-gray-500 cursor-not-allowed' : ''}
                  ${isCurrentDayHoliday && !isMonday ? 'bg-yellow-100 border-2 border-yellow-500' : ''}
                  `}
                  onClick={() => {
                    if (isFlexibleStaffEditing && isCurrentMonth && day && !isMonday) {
                      toggleFlexibleStaffAvailability(editingFlexibleStaffId, day);
                    }
                  }}
                >
                  {day && (
                    <>
                      <span className="text-lg font-semibold">{day.getDate()}</span>
                      <span className="text-sm text-indigo-600 font-medium mt-1">
                        {generatedShift[formatDate(day)]?.map((s, idx) => (
                          <div key={idx} className="text-xs">
                            {s.staff} {s.startTime && s.endTime ? `(${s.startTime} - ${s.endTime})` : ''}
                          </div>
                        ))}
                      </span>
                    </>
                  )}
                </div>
              );
            })}
          </div>
          {editingFlexibleStaffId && (
            <div className="text-center mt-4">
              <button
                onClick={() => {
                  setEditingFlexibleStaffId(null);
                }}
                className="w-full bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-6 rounded-lg shadow-md transform hover:scale-105 transition duration-200 ease-in-out"
              >
                日付設定を終了
              </button>
            </div>
          )}
        </section>
      </div>
      <ToastMessage message={toastMessage} show={showToast} type={toastType} />
      <ConfirmationModal
        isOpen={isClearConfirmModalOpen}
        message="全てのスタッフ情報とシフト情報を削除してもよろしいですか？この操作は元に戻せません。"
        onConfirm={confirmClearData}
        onCancel={cancelClearData}
      />
      <ConfirmationModal
        isOpen={isDeleteStaffConfirmModalOpen}
        message={`${staff.find(s => s.id === staffIdToDelete)?.name} を本当に削除してもよろしいですか？`}
        onConfirm={confirmDeleteStaff}
        onCancel={cancelDeleteStaff}
      />
      <ConfirmationModal
        isOpen={isClearCurrentMonthShiftConfirmModalOpen}
        message="当月のシフトデータを全てクリアしてもよろしいですか？この操作は元に戻せません。"
        onConfirm={confirmClearCurrentMonthShift}
        onCancel={cancelClearCurrentMonthShift}
      />
    </div>
  );
};

export default App;
