$(document).ready(function () {
  var $toggle = $('#chatbot-toggle');
  var $window = $('#chatbot-window');
  var $close = $window.find('.chatbot-close');
  var $messages = $('#chatbot-messages');
  var $form = $('#chatbot-form');
  var $input = $('#chatbot-input');

  var booking = null;

  function scrollToBottom() {
    $messages.scrollTop($messages[0].scrollHeight);
  }

  function addMessage(text, sender) {
    var safeText = $('<div/>').text(text).html();
    var $msg = $('<div class="chatbot-message ' + sender + '"><div class="chatbot-bubble">' + safeText + '</div></div>');
    $messages.append($msg);
    scrollToBottom();
  }

  function resetBooking() {
    booking = null;
  }

  function startBookingFlow() {
    booking = {
      step: 'name',
      data: {}
    };
    addMessage("Great, let's book an appointment. What is your full name?", 'bot');
  }

  function handleBookingStep(text) {
    if (!booking) return;

    if (booking.step === 'name') {
      booking.data.full_name = text.trim();
      var parts = booking.data.full_name.split(' ');
      booking.data.pat_first_name = parts[0];
      booking.data.pat_last_name = parts.slice(1).join(' ') || parts[0];
      booking.step = 'insurance';
      addMessage("Thanks " + booking.data.full_name + ". What is your insurance number?", 'bot');
      return;
    }

    if (booking.step === 'insurance') {
      booking.data.pat_insurance_no = text.trim();
      booking.step = 'phone';
      addMessage("Got it. What is your phone number?", 'bot');
      return;
    }

    if (booking.step === 'phone') {
      booking.data.pat_ph_no = text.trim();
      booking.step = 'address';
      addMessage("And finally, please share your address.", 'bot');
      return;
    }

    if (booking.step === 'address') {
      booking.data.pat_address = text.trim();
      booking.step = 'date';
      addMessage("On which date would you like the appointment? Please use YYYY-MM-DD.", 'bot');
      return;
    }

    if (booking.step === 'date') {
      booking.data.appointment_date = text.trim();
      booking.step = 'doctor';
      addMessage("Do you have a preferred doctor ID? If not, type 1.", 'bot');
      return;
    }

    if (booking.step === 'doctor') {
      var doctorId = parseInt(text.trim(), 10);
      if (!doctorId || doctorId < 1) {
        doctorId = 1;
      }
      booking.data.doc_id = doctorId;
      booking.step = 'confirm';

      addMessage(
        "Perfect. I will book an appointment for " +
        booking.data.full_name +
        " on " + booking.data.appointment_date +
        " with doctor ID " + booking.data.doc_id +
        ". Type 'yes' to confirm or 'cancel' to abort.",
        'bot'
      );
      return;
    }

    if (booking.step === 'confirm') {
      var lower = text.trim().toLowerCase();
      if (lower === 'cancel') {
        addMessage('Okay, I have cancelled this booking flow.', 'bot');
        resetBooking();
        return;
      }
      if (lower !== 'yes') {
        addMessage("Please type 'yes' to confirm or 'cancel' to abort.", 'bot');
        return;
      }
      createAppointment();
      return;
    }
  }

  function createAppointment() {
    if (!booking) return;

    var patientPayload = {
      pat_first_name: booking.data.pat_first_name,
      pat_last_name: booking.data.pat_last_name,
      pat_insurance_no: booking.data.pat_insurance_no,
      pat_ph_no: booking.data.pat_ph_no,
      pat_address: booking.data.pat_address
    };

    addMessage('Creating your patient profile…', 'bot');

    $.ajax({
      url: '/patient',
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify(patientPayload)
    }).done(function (patientResponse) {
      var patientId = patientResponse.pat_id;
      if (!patientId) {
        addMessage('Something went wrong while creating the patient record.', 'bot');
        resetBooking();
        return;
      }

      addMessage('Patient profile created. Booking the appointment…', 'bot');

      var appointmentPayload = {
        pat_id: patientId,
        doc_id: booking.data.doc_id,
        appointment_date: booking.data.appointment_date
      };

      $.ajax({
        url: '/appointment',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(appointmentPayload)
      }).done(function () {
        addMessage(
          'Your appointment has been booked for ' +
          booking.data.appointment_date +
          ' with doctor ID ' +
          booking.data.doc_id +
          '.',
          'bot'
        );
        resetBooking();
      }).fail(function () {
        addMessage('Unable to book the appointment right now. Please try again from the dashboard.', 'bot');
        resetBooking();
      });
    }).fail(function () {
      addMessage('Unable to create the patient record. Please try again later.', 'bot');
      resetBooking();
    });
  }

  function handleUserInput(text) {
    var trimmed = text.trim();
    if (!trimmed) {
      return;
    }

    addMessage(trimmed, 'user');

    if (!booking) {
      var lower = trimmed.toLowerCase();
      if (lower.indexOf('appointment') !== -1 || lower.indexOf('book') !== -1 || lower.indexOf('schedule') !== -1) {
        startBookingFlow();
      } else {
        addMessage('I can help you book an appointment. Try saying "Book me an appointment".', 'bot');
      }
    } else {
      handleBookingStep(trimmed);
    }
  }

  $toggle.on('click', function () {
    $window.toggleClass('hidden');
    if (!$window.hasClass('hidden') && $messages.children().length === 0) {
      addMessage('Hi, I am the MedSync assistant. I can help you book an appointment.', 'bot');
      addMessage('For example, type "Book me an appointment".', 'bot');
    }
    if (!$window.hasClass('hidden')) {
      $input.focus();
    }
  });

  $close.on('click', function () {
    $window.addClass('hidden');
  });

  $form.on('submit', function (e) {
    e.preventDefault();
    var text = $input.val();
    $input.val('');
    handleUserInput(text);
  });
});

